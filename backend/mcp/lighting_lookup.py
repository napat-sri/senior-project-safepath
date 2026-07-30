import json
import math
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent / "data"
LAMPS_PATH = DATA_DIR / "berlin_street_lamps.json"

# Recalibrated from a 3,000-point random sample across Berlin (see
# Docs/RouteScoringTestCases.md for the methodology), filtered to points
# within 300m of any lamp ("near-road" — excludes lakes/forest interior a
# route would never actually cross). The old ceiling (600) was set from a
# single outlier test point (Potsdamer Platz, ~750/km2, the single brightest
# plaza in the city), which meant almost nowhere else — including perfectly
# safe, normal streets — could score above ~50-60. The new ceiling is the
# 90th percentile of that near-road sample (~382/km2): only the top 10% of
# real street-level locations should hit 100, everything else scales
# relative to a realistic "well-lit" baseline instead of the single
# brightest point in Berlin.
LAMPS_PER_KM2_LOW = 0
LAMPS_PER_KM2_HIGH = 380

_lamps = None  # loaded once, lazily


def _load_lamps():
    global _lamps
    if _lamps is not None:
        return _lamps
    with open(LAMPS_PATH, encoding="utf-8") as f:
        data = json.load(f)
    _lamps = [(el["lat"], el["lon"]) for el in data["elements"] if "lat" in el and "lon" in el]
    return _lamps


def haversine_m(lat1, lng1, lat2, lng2):
    r = 6_371_000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def normalize_score(value, lo, hi):
    pct = (value - lo) / (hi - lo)
    pct = max(0.0, min(1.0, pct))
    return round(pct * 100)


def lighting_density(lat, lng, radius_m=150):
    lamps = _load_lamps()
    lamp_count = sum(1 for lat2, lng2 in lamps if haversine_m(lat, lng, lat2, lng2) <= radius_m)

    area_km2 = (math.pi * radius_m ** 2) / 1_000_000
    density = lamp_count / area_km2
    score = normalize_score(density, LAMPS_PER_KM2_LOW, LAMPS_PER_KM2_HIGH)

    return {
        "lamp_count": lamp_count,
        "radius_m": radius_m,
        "lamps_per_km2": round(density, 1),
        "lighting_safety_score": score,
    }


if __name__ == "__main__":
    print("Alexanderplatz:", lighting_density(52.5219, 13.4132))
    print("Potsdamer Platz:", lighting_density(52.5096, 13.3759))
    print("Grunewald forest interior:", lighting_density(52.4740, 13.2170))