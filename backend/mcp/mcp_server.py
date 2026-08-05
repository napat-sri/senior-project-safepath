
import asyncio
from pathlib import Path

import accident_lookup
import crime_lookup
import lighting_lookup
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

DATA_DIR = Path(__file__).resolve().parent / "data"


security = TransportSecuritySettings(
    enable_dns_rebinding_protection=True,
    # "mcp" is the service/hostname other containers use per docker-compose(.dev).yml;
    # "safepath-mcp" is kept too in case a compose file names the service that instead.
    allowed_hosts=["mcp:8000", "safepath-mcp:8000", "localhost:8000", "127.0.0.1:8000"],
    allowed_origins=[
        "http://mcp:8000", "http://safepath-mcp:8000",
        "http://localhost:8000", "http://127.0.0.1:8000",
    ],
)

mcp = FastMCP("safepath-data", host="0.0.0.0", port=8000, transport_security=security)

# Load everything once at startup, not per-request.
_crime_table = crime_lookup.load_crime_table()
_polygons = crime_lookup.load_polygons()
# Score from crimes-per-km2, not crimes-per-100k-residents — see the FIX note
# in crime_lookup.py for why (population denominator distorts low-resident,
# high-foot-traffic districts like Alexanderplatz/Regierungsviertel).
crime_lookup.attach_density(_crime_table, _polygons)
_dens_min, _dens_max = crime_lookup.build_normalization(_crime_table)

_accidents = accident_lookup.load_berlin_accidents([
    DATA_DIR / "Unfallorte_2021_LinRef.txt",
    DATA_DIR / "Unfallorte2022_LinRef.csv",
    DATA_DIR / "Unfallorte2023_LinRef.csv",
    DATA_DIR / "Unfallorte2024_LinRef.csv",
    DATA_DIR / "Unfallorte_2025_LR_BasisDLM.csv",
])


@mcp.tool()
def get_crime_data(lat: float, lng: float) -> dict:
    """Real Berlin crime rate (Kriminalitätsatlas) for a coordinate.
    Returns the Bezirksregion name, cases per 100k residents, and a
    0-100 crime_safety_score (100 = lowest crime)."""
    return crime_lookup.crime_score(lat, lng, _crime_table, _polygons, _dens_min, _dens_max)

_overpass_semaphore = asyncio.Semaphore(4)  # cap concurrent Overpass calls, don't hammer it

async def _lighting_bounded(lat, lng, radius_m=150):
    async with _overpass_semaphore:
        return await lighting_lookup.lighting_density_async(lat, lng, radius_m)

@mcp.tool()
def get_lighting_density(lat: float, lng: float, radius_m: int = 150) -> dict:
    """Real OpenStreetMap street-lamp density near a coordinate (pre-fetched, in-memory)."""
    return lighting_lookup.lighting_density(lat, lng, radius_m)

@mcp.tool()
def get_accident_risk(lat: float, lng: float, radius_m: int = 150) -> dict:
    """Real accident history (Unfallatlas, 2021-2025) near a coordinate.
    Returns accident count, severity-weighted risk points, and a 0-100
    accident_safety_score (100 = no nearby accident history)."""
    return accident_lookup.accident_risk(lat, lng, _accidents, radius_m)

'''
@mcp.tool()
def get_route_safety_context(coordinates: list[list[float]], sample_every_m: int = 300) -> dict:
    """Crime + lighting + accident data sampled along a full route polyline."""
    samples = _sample_polyline(coordinates, sample_every_m)
    if not samples:
        return {"found": False, "message": "No coordinates provided."}

    results = []
    for lat, lng in samples:
        crime = crime_lookup.crime_score(lat, lng, _crime_table, _polygons, _dens_min, _dens_max)
        lighting = lighting_lookup.lighting_density(lat, lng)
        accident = accident_lookup.accident_risk(lat, lng, _accidents)
        results.append({
            "lat": lat, "lng": lng,
            "crime_safety_score": crime.get("crime_safety_score"),
            "lighting_safety_score": lighting.get("lighting_safety_score"),
            "accident_safety_score": accident.get("accident_safety_score"),
        })

    def avg(key):
        vals = [r[key] for r in results if r[key] is not None]
        return round(sum(vals) / len(vals)) if vals else None

    return {
        "sample_count": len(results),
        #"samples": results,
        "avg_crime_safety_score": avg("crime_safety_score"),
        "avg_lighting_safety_score": avg("lighting_safety_score"),
        "avg_accident_safety_score": avg("accident_safety_score"),
    }
'''
@mcp.tool()
def get_routes_safety_context(routes: list[dict], sample_every_m: int = 300) -> dict:
    """Crime + lighting + accident data for MULTIPLE routes in ONE call.

    routes: list of {"id": str, "coordinates": [[lat, lng], ...]} — pass ALL
    route alternatives together, not one call per route. Returns a dict keyed
    by route id with avg_crime_safety_score, avg_lighting_safety_score, and
    avg_accident_safety_score for each.
    """
    output = {}
    for route in routes:
        route_id = route.get("id")
        coordinates = route.get("coordinates", [])
        samples = _sample_polyline(coordinates, sample_every_m)
        if not samples:
            output[route_id] = {"found": False, "message": "No coordinates provided."}
            continue

        crime_scores, lighting_scores, accident_scores = [], [], []
        for lat, lng in samples:
            crime = crime_lookup.crime_score(lat, lng, _crime_table, _polygons, _dens_min, _dens_max)
            lighting = lighting_lookup.lighting_density(lat, lng)
            accident = accident_lookup.accident_risk(lat, lng, _accidents)
            if crime.get("crime_safety_score") is not None:
                crime_scores.append(crime["crime_safety_score"])
            if lighting.get("lighting_safety_score") is not None:
                lighting_scores.append(lighting["lighting_safety_score"])
            if accident.get("accident_safety_score") is not None:
                accident_scores.append(accident["accident_safety_score"])

        def avg(vals):
            return round(sum(vals) / len(vals)) if vals else None

        output[route_id] = {
            "sample_count": len(samples),
            "avg_crime_safety_score": avg(crime_scores),
            "avg_lighting_safety_score": avg(lighting_scores),
            "avg_accident_safety_score": avg(accident_scores),
        }
    return output

def _sample_polyline(coordinates, every_m):
    if not coordinates:
        return []
    if len(coordinates) == 1:
        return [tuple(coordinates[0])]
    samples = [tuple(coordinates[0])]
    dist = 0.0
    prev = coordinates[0]
    for point in coordinates[1:]:
        dist += lighting_lookup.haversine_m(prev[0], prev[1], point[0], point[1]) if hasattr(lighting_lookup, "haversine_m") else accident_lookup.haversine_m(prev[0], prev[1], point[0], point[1])
        if dist >= every_m:
            samples.append(tuple(point))
            dist = 0.0
        prev = point
    if samples[-1] != tuple(coordinates[-1]):
        samples.append(tuple(coordinates[-1]))
    return samples


if __name__ == "__main__":
    # _accidents is a dict of numpy arrays (lats/lngs/severities) since the
    # accident_risk() vectorization — len() on it would give the wrong number
    # (3, the dict's key count) rather than the accident count.
    print(f"Loaded {len(_crime_table)} crime regions, {len(_accidents['lats'])} accidents.")
    mcp.run(transport="sse")