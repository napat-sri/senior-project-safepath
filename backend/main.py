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

app = FastAPI(title="SafePath API")

# Allow the Vue dev server to call this API from the browser.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://127.0.0.1:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Public OSRM demo server. NOTE: it only offers the *driving* profile, which is
# fine to get routes on the map now. For a pedestrian "safe walking" app we'll
# later switch to a walking profile (self-hosted OSRM-foot or OpenRouteService).
OSRM_URL = "https://router.project-osrm.org/route/v1/driving"


class Point(BaseModel):
    lat: float
    lng: float

class RouteRequest(BaseModel):
    start: Point
    destination: Point


@app.get("/")
def root():
    return {"message": "Welcome to SafePath API"}


@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.get("/api/test")
def test():
    return {"data": [{"id": 1,"name": "Route 1"}, {"id": 2,"name": "Route 2"}, {"id": 3,"name": "Route 3"   }]}

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
    params = {
        "q": query,
        "format": "json",
        "limit": 5, 
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




FLOW_ID = "63a16f8d-0f9e-4930-91c0-e41ec7e842fd" 
LANGFLOW_URL = f"http://langflow:7860/api/v1/run/{FLOW_ID}" 

@app.post("/api/routes/safe")
async def get_safe_routes(req: RouteRequest):
    """
    1. Fetches candidate routes from OSRM.
    2. Sends route summaries to Langflow for safety analysis.
    3. Returns the winning route, reasoning, and map coordinates to the frontend.
    """
    s, d = req.start, req.destination
    osrm_url = f"{OSRM_URL}/{s.lng},{s.lat};{d.lng},{d.lat}"
    params = {"overview": "full", "geometries": "geojson", "alternatives": "true"}

    # --- STEP 1: Get Raw Routes from OSRM ---
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(osrm_url, params=params, timeout=20.0)
            resp.raise_for_status()
            osrm_data = resp.json()
        except httpx.HTTPError as exc:
            raise HTTPException(status_code=502, detail=f"Routing service error: {exc}")

    if osrm_data.get("code") != "Ok" or not osrm_data.get("routes"):
        raise HTTPException(status_code=404, detail="No routes found.")

    routes = []
    llm_summaries = [] # This is what we will send to Langflow

    for i, route in enumerate(osrm_data["routes"]):
        route_id = f"route-{i + 1}"
        coords = [[lat, lng] for lng, lat in route["geometry"]["coordinates"]]
        
        # Save the full data for the frontend
        routes.append({
            "id": route_id,
            "geometry": coords,
            "distance_m": round(route["distance"]),
            "duration_s": round(route["duration"]),
        })
        
        # Save a lightweight summary for the AI
        llm_summaries.append({
            "id": route_id,
            "distance_meters": round(route["distance"]),
            "duration_seconds": round(route["duration"]),
            # Note: In a real scenario, you'd add hazard data or street names here!
        })

    # --- STEP 2: Ask Langflow for the Safest Route ---
    # We ask Langflow to return a strict JSON response
    
    
    # prompt = f"""
    # Analyze these routes and pick the safest one for a pedestrian. 
    # Right now, just pick the shortest/fastest one as a baseline.
    # Routes: {json.dumps(llm_summaries)}
    
    # You MUST return your answer in this exact JSON format:
    # {{"recommended_route_id": "route-X", "reasoning": "Explain why here."}}
    # """

    # langflow_payload = {
    #     "input_value": prompt,
    #     "output_type": "chat",
    #     "input_type": "chat",
    # }
    
    prompt = f"""
    You are SafePath Berlin, a safety-first navigation assistant for students, tourists, and commuters.
    Routes:
    {json.dumps(llm_summaries)}

    Rank ALL routes from safest to least safe. For each route explain:
    - Why it is safer or riskier than the others (lighting, crime exposure, road type, time on exposed streets)
    - Any trade-offs (e.g. slightly longer but significantly safer)
    - One practical tip for travelling this route

     You MUST return your answer in this exact JSON format:
     {{
        "ranked_routes": [
            {{
            "route_id": "route-X",
            "rank": 1,
            "safety_score": <0-100, higher = safer>,
            "reasoning": "2-3 sentences on why this rank.",
            "trade_offs": "e.g. 4 min longer but avoids Hermannplatz at night.",
            "tip": "One practical tip for this specific route."
            }}
        ],
        "recommended_route_id": "route-X",
        "summary": "One sentence explaining the overall recommendation."
    }}"""

    langflow_payload = {
    "input_value": prompt,
    "output_type": "chat",
    "input_type": "chat",
    "tweaks": {
        "Agent-xyz": {
            "system_message": (
                "You are SafePath Berlin. Always prioritise personal safety over speed. "
                "Never recommend a route purely because it is shortest or fastest. "
                "Return only valid JSON."
            )
        }
    }
}

    async with httpx.AsyncClient() as client:
        try:
            lf_resp = await client.post(LANGFLOW_URL, json=langflow_payload, timeout=30.0)
            lf_resp.raise_for_status()
            lf_data = lf_resp.json()
            
            # Extract the AI's text response (You may need to adjust this path based on your specific Langflow output structure)
            ai_message = lf_data["outputs"][0]["outputs"][0]["results"]["message"]["text"]
            
            # Parse the AI's JSON output
            ai_decision = json.loads(ai_message)
            
        except (httpx.HTTPError, KeyError, json.JSONDecodeError) as exc:
            # Fallback if Langflow fails or returns bad formatting
            ai_decision = {
                "recommended_route_id": "route-1",
                "reasoning": f"Defaulted to route-1. AI analysis failed: {exc}"
            }

    # --- STEP 3: Combine and Return ---
    return {
        "ai_recommendation": ai_decision,
        "all_routes": routes
    }