"""SafePath API.

Endpoints:
  GET  /             - banner
  GET  /api/health   - liveness check
  POST /api/routes   - candidate routes between two points (via OSRM)
"""

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import re
import time

import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="SafePath API")

# Allow the Vue dev server to call this API from the browser.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://safepath.duckdns.org",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://172.28.0.20:8080",  # frontend loaded over the WireGuard VPN
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Public OSRM demo server. NOTE: it only offers the *driving* profile, which is
# fine to get routes on the map now. For a pedestrian "safe walking" app we'll
# later switch to a walking profile (self-hosted OSRM-foot or OpenRouteService).
OSRM_URL = "https://router.project-osrm.org/route/v1/driving"
OSRM_FOOT_URL = "https://router.project-osrm.org/route/v1/foot"
FLOW_ID = os.getenv("VUE_APP_LANGFLOW_ROUTE_AGENT_FLOW_ID")
#LANGFLOW_URL = f"http://langflow:7860/api/v1/run/{FLOW_ID}" 
LANGFLOW_URL = f"https://langflow.safepath.duckdns.org/api/v1/run/{FLOW_ID}" 
# Authentication Key for Langflow (Required if login is enabled in the Langflow UI)
LANGFLOW_API_KEY = os.getenv("VUE_APP_LANGFLOW_API_KEY")




class Point(BaseModel):
    lat: float
    lng: float

class RouteRequest(BaseModel):
    start: Point
    destination: Point
    startName: str | None = None
    destinationName: str | None = None


@app.get("/")
def root():
    return {"message": "Welcome to SafePath API"}


@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.get("/api/test")
def test():
    return {"data": [{"id": 1,"name": "Route 1"}, {"id": 2,"name": "Route 2"}, {"id": 3,"name": "Route 3"   }]}

@app.get("/api/langflow/health")
def langflow_health():
    return {
        "status": "ok",
        "langflow_target": LANGFLOW_URL,
        "auth_configured": LANGFLOW_API_KEY
    }

@app.get("/api/places")
def search_places(query: str):
    """
    Search for locations by name using OpenStreetMap's Nominatim API.
    Returns a clean list of places with lat/lng for frontend dropdowns.
    """
    # Don't bother searching if the user only typed 1 or 2 letters
    if not query or len(query) < 3:
        return {"places": []}

    url = "https://nominatim.openstreetmap.org/search"
    # params = {
    #     "q": query,
    #     "format": "json",
    #     "limit": 5, 
    # }
    params = {
        "q": query,
        "format": "json",
        "limit": 5, 
        "countrycodes": "de",                          # Germany only
        "viewbox":      "13.0883,52.3383,13.7611,52.6755",  # Berlin bounding box
        "bounded":      1,          
    }
    
    # IMPORTANT: Nominatim requires a User-Agent header, otherwise they block the request.
    headers = {
        "User-Agent": "SafePath_SeniorProject/1.0 (Student Project)"
    }

    try:
        resp = httpx.get(url, params=params, headers=headers, timeout=10.0)
        resp.raise_for_status()
        data = resp.json()
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"Geocoding service error: {exc}")


    places = []
    for item in data:
        places.append({
           
            "name": item.get("display_name"), 
            "lat": float(item.get("lat")),
            "lng": float(item.get("lon"))
        })

    return {"places": places}

'''
@app.post("/api/routes")
def get_routes(req: RouteRequest):
    """Return candidate routes between start and destination.

    Calls OSRM with alternatives enabled and normalises the response into a
    small shape the frontend can draw directly. Coordinates are returned as
    [lat, lng] pairs (OSRM gives [lng, lat], so we swap).
    """
    s, d = req.start, req.destination
    url = f"{OSRM_URL}/{s.lng},{s.lat};{d.lng},{d.lat}"
    params = {"overview": "full", "geometries": "geojson", "alternatives": "true"}

    try:
        resp = httpx.get(url, params=params, timeout=20.0)
        resp.raise_for_status()
        data = resp.json()
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"Routing service error: {exc}")

    if data.get("code") != "Ok" or not data.get("routes"):
        raise HTTPException(
            status_code=404, detail="No route found between those points."
        )

    routes = []
    for i, route in enumerate(data["routes"]):
        coords = [[lat, lng] for lng, lat in route["geometry"]["coordinates"]]
        routes.append(
            {
                "id": f"route-{i + 1}",
                "geometry": coords,
                "distance_m": round(route["distance"]),
                "duration_s": round(route["duration"]),
            }
        )

    return {"routes": routes}
'''




@app.post("/api/routes/safe")
async def get_safe_routes(req: RouteRequest):
    api_start = time.perf_counter()
    """
    1. Fetches candidate routes from OSRM.
    2. Sends route summaries to Langflow for safety analysis.
    3. Returns the winning route, reasoning, and map coordinates to the frontend.
    """
    s, d = req.start, req.destination
    osrm_url = f"{OSRM_URL}/{s.lng},{s.lat};{d.lng},{d.lat}"
    params = {"overview": "full","geometries": "geojson","alternatives": "true"}

    # ---------------------------------------------------
    # STEP 1: FETCH ROUTES FROM OSRM
    # ---------------------------------------------------
    osrm_start = time.perf_counter()
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(osrm_url,params=params,timeout=20.0)
            osrm_end = time.perf_counter()
            print(
                f"[TIME] OSRM request: "
                f"{osrm_end - osrm_start:.2f} sec"
            )
            resp.raise_for_status()
            osrm_data = resp.json()
        except httpx.HTTPError as exc:
            raise HTTPException(
                status_code=502,
                detail=f"Routing service error: {exc}"
            )

    if osrm_data.get("code") != "Ok":
        raise HTTPException(status_code=404,detail="No routes found.")

    raw_routes = osrm_data.get("routes", [])
    if not raw_routes:
        raise HTTPException(
            status_code=404,
            detail="No routes found."
        )

    routes = []
    llm_summaries = [] # Send to Langflow
    process_routes_start = time.perf_counter()
    for i, route in enumerate(raw_routes):
        route_id = f"route-{i+1}"
        coordinates = [
            [lat, lng]
            for lng, lat in route["geometry"]["coordinates"]
        ]

        distance_km = round(route["distance"] / 1000, 1)
        duration_min = round(route["duration"] / 60)

        backend_route = {
            "id": route_id,
            "coordinates": coordinates,
            "distance": f"{distance_km} km",
            "duration": f"{duration_min} min",
            "distance_m": round(route["distance"]),
            "duration_s": round(route["duration"]),
        }

        routes.append(backend_route)

        # Only lightweight data to AI
        llm_summaries.append({
            "id": route_id,
            "distance_km": distance_km,
            "duration_min": duration_min
        })
    
    process_routes_end = time.perf_counter()
    print(
    f"[TIME] Route processing: "
    f"{process_routes_end - process_routes_start:.2f} sec"
)
    # ---------------------------------------------------
    # STEP 2: AI SAFETY ANALYSIS
    # ---------------------------------------------------

    prompt = f""" You are SafePath Berlin, a safety-first navigation assistant for students, tourists, and commuters in Berlin.
    FROM:
    {s.lat}, {s.lng}
    TO:
    {d.lat}, {d.lng}

    ROUTES:
    {json.dumps(llm_summaries, indent=2)}
    Rules:
    - accident risk 35%
    - crime level 35%
    - street lighting 30%

    Color:
    85+ = #10B981
    70-84 = #F59E0B
    <70 = #EF4444    
    Return ONLY valid JSON array.
    [
    {{
        "id": "route-1",
        "name": "Route 1",
        "safetyScore": 85,
        "summary": "2 sentences: why this rank and one trade-off vs the other routes.",
        "accentColor": "<hex per rules above>",
        "breakdown": [
        {{
            "label": "Accident Risk",
            "score": 80
        }},
        {{
            "label": "Crime Level",
            "score": 90
        }},
        {{
            "label": "Street Lighting",
            "score": 85
        }}
        ]
    }}
    ]
    """

    langflow_payload = {
        "input_value": prompt,
        "output_type": "chat",
        "input_type": "chat",
    }
    # Setup headers, injecting API keys securely if available
    headers = {
        "Content-Type": "application/json"
    }
    if LANGFLOW_API_KEY:
        headers["x-api-key"] = LANGFLOW_API_KEY
        print("[LANGFLOW] Auth initialized with API Key.")
    else:
        print("[LANGFLOW] WARNING: No API Key found in .env. Requests will fail if Langflow has login enabled.")

    ai_routes = []
    async with httpx.AsyncClient() as client:
        try:
            langflow_start = time.perf_counter()
            lf_resp = await client.post(
                LANGFLOW_URL,
                json=langflow_payload,
                headers=headers,
                timeout=45.0
            )

            lf_resp.raise_for_status()
            langflow_end = time.perf_counter()
            print(
                f"[TIME] Langflow request: "
                f"{langflow_end - langflow_start:.2f} sec"
            )
            lf_data = lf_resp.json()
            json_parse_start = time.perf_counter()
            raw_text = (
                lf_data["outputs"][0]
                ["outputs"][0]
                ["results"]["message"]["text"]
            )

            # ---------------------------------------------
            # CLEAN AI RESPONSE
            # ---------------------------------------------

            raw_text = raw_text.strip()
            # Remove markdown fences
            raw_text = re.sub(
                r"^```(?:json)?|```$",
                "",
                raw_text,
                flags=re.MULTILINE
            ).strip()

            # Extract JSON array safely
            match = re.search(r"\[.*\]", raw_text, re.DOTALL)
            if not match:
                raise ValueError("No JSON array found")

            json_text = match.group(0)
            ai_routes = json.loads(json_text)
            json_parse_end = time.perf_counter()
            print(
                f"[TIME] JSON parsing: "
                f"{json_parse_end - json_parse_start:.2f} sec"
            )
            if not isinstance(ai_routes, list):
                raise ValueError("AI response is not a list")

        except Exception as exc:
            print("Langflow parsing error:", exc)
            ai_routes = []

    # ---------------------------------------------------
    # STEP 3: MERGE AI + OSRM DATA
    # ---------------------------------------------------

    route_lookup = {
        route["id"]: route
        for route in routes
    }

    route_suggestions = []
    merge_start = time.perf_counter()
    if ai_routes:
        for ai_route in ai_routes:
            route_id = ai_route.get("id")
            backend_route = route_lookup.get(route_id)
            if not backend_route:
                continue

            route_suggestions.append({
                "id": route_id,
                "name": ai_route.get(
                    "name",
                    route_id
                ),
                "origin": f"{s.lat:.4f}, {s.lng:.4f}",
                "destination": f"{d.lat:.4f}, {d.lng:.4f}",
                "routeType": ai_route.get("routeType", "driving"),
                "safetyScore": ai_route.get(
                    "safetyScore",
                    50
                ),

                "distance": backend_route["distance"],
                "duration": backend_route["duration"],
                "summary": ai_route.get(
                    "summary",
                    "No analysis available."
                ),
                "accentColor": ai_route.get(
                    "accentColor",
                    "#F59E0B"
                ),
                "coordinates": backend_route["coordinates"],
                "breakdown": ai_route.get(
                    "breakdown",
                    []
                )
            })
    merge_end = time.perf_counter()

    print(
        f"[TIME] Merge routes: "
        f"{merge_end - merge_start:.2f} sec"
    )
    # ---------------------------------------------------
    # FALLBACK
    # ---------------------------------------------------

    if not route_suggestions:
        for i, route in enumerate(routes):
            route_suggestions.append({
                "id": route["id"],
                "name": f"Route {i+1}",
                "origin": f"{s.lat:.4f}, {s.lng:.4f}",
                "destination": f"{d.lat:.4f}, {d.lng:.4f}",
                "safetyScore": 50,
                "distance": route["distance"],
                "duration": route["duration"],
                "routeType": "driving",
                "summary": "AI analysis unavailable. Showing raw route data.",
                "accentColor": "#F59E0B",
                "coordinates": route["coordinates"],
                "breakdown": [
                    {
                        "label": "Accident Risk",
                        "score": 50
                    },
                    {
                        "label": "Crime Level",
                        "score": 50
                    },
                    {
                        "label": "Street Lighting",
                        "score": 50
                    }
                ]
            })
    api_end = time.perf_counter()

    print(
        f"[TIME] TOTAL API: "
        f"{api_end - api_start:.2f} sec"
    )
    return {
        "route_suggestions": route_suggestions
    }



