# main fixed AI
"""SafePath API.

Endpoints:
    
    Static endpoints:
    Get / :display a welcome message.
    Get /api/health :check the health of the API.
    Get /api/langflow/health :check the health of the Langflow service.
    Get /api/monitor/health :check the health of the Langfuse monitoring service.
    
    Langfuse monitoring endpoints (read-only):
    Get /api/monitor/traces :fetch recent traces from Langfuse.
    Get /api/monitor/traces/{trace_id} :fetch detailed information for a specific trace.
    Get /api/monitor/alerts :fetch alerts from Langfuse.
    Get /api/monitor/stats :fetch aggregated statistics from Langfuse.
    Get /api/monitor/export :export recent traces from Langfuse in CSV or JSON format.
    
    Admin endpoints (read-only, sourced from Langfuse):
    Get /api/admin/search-logs :fetch user route-search logs for the admin table.

    SafePath routing endpoints:
    Get /api/places :search for locations by name using LocationIQ's Autocomplete API.
    Get /api/routes/safe :fetch safe routes between two points, scored by AI for safety.
    

"""

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel,Field
import csv
import io
import json
import time
import uuid
from datetime import datetime, timezone

import os
from dotenv import load_dotenv

import langfuse_monitor
import langfuse_prompts
import langfuse_search_logs

from typing import List, Optional
from openai import AsyncOpenAI
LITELLM_PROXY_URL = os.getenv("LITELLM_PROXY_URL")# default for local dev
LITELLM_VIRTUAL_KEY = os.getenv("LITELLM_VIRTUAL_KEY")# default for local dev
litellm_client = AsyncOpenAI(
    base_url=LITELLM_PROXY_URL,    
    api_key=LITELLM_VIRTUAL_KEY,  
)


load_dotenv()

app = FastAPI(title="SafePath API")

# Allow the Vue dev server to call this API from the browser.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://safepath.duckdns.org",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
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
LANGFLOW_URL = f"http://langflow:7860/api/v1/run/{FLOW_ID}" 
# Authentication Key for Langflow (Required if login is enabled in the Langflow UI)
LANGFLOW_API_KEY = os.getenv("VUE_APP_LANGFLOW_API_KEY")
# LocationIQ API Key for geocoding (autocomplete) requests. Required.
LOCATIONIQ_API_KEY = os.getenv("LOCATIONIQ_API_KEY")

# ---------------------------------------------------------------------------
# Route-safety prompt fallback.
#
# The live prompt is managed in Langfuse under the name
# `safepath-route-safety` and fetched at request time (see langfuse_prompts).
# This string is the exact same text and is used only if Langfuse is
# unreachable, so routing keeps working. Keep the two copies in sync
# (Docs/langfuse-prompts.md has the canonical version to paste into the UI).
#
# Variables use Langfuse mustache syntax: {{from_lat}}, {{from_lng}},
# {{to_lat}}, {{to_lng}}, {{routes_json}}. Single braces are literal JSON.
# ---------------------------------------------------------------------------
FALLBACK_ROUTE_PROMPT = """You are SafePath Berlin, a safety-first navigation assistant for students, tourists, and commuters in Berlin.

Your ENTIRE response MUST be ONLY a JSON array — it must start with [ and end with ]. Do NOT include any reasoning, explanation, calculations, markdown, or any text before or after the array.

FROM:
{{from_lat}}, {{from_lng}}
TO:
{{to_lat}}, {{to_lng}}

ROUTES:
{{routes_json}}

Scoring weights: accident risk 35%, crime level 35%, street lighting 30%.
Every score (safetyScore and each breakdown score) MUST be an integer from 0 to 100.
accentColor MUST be exactly one of these, chosen from the route's safetyScore:
  "#0B8043" for 85+, "#E8590C" for 70-84, "#C1121F" for below 70.

Rules:
- Never use placeholders, dashes (---), dots (.), null, or blanks. Every field must have a real value.
- Return one object per route in the ROUTES input, keeping the same "id".

Example of the exact format (values illustrative only):
[
  {
    "id": "route-1",
    "name": "Route 1",
    "safetyScore": 85,
    "summary": "Two sentences: why this rank, and one trade-off vs the other routes.",
    "accentColor": "#0B8043",
    "breakdown": [
      { "label": "Accident Risk", "score": 80 },
      { "label": "Crime Level", "score": 90 },
      { "label": "Street Lighting", "score": 85 }
    ]
  }
]

Output ONLY the JSON array. Your first character must be [ and your last character must be ].
"""

class Point(BaseModel):
    lat: float
    lng: float

class RouteRequest(BaseModel):
    start: Point
    destination: Point
    # Anonymous identity for Langfuse tracking (no auth yet). The frontend
    # sends a stable guest id as user_id and a per-visit id as session_id.
    # Optional so older/other clients keep working.
    user_id: str | None = None
    session_id: str | None = None
    startName: str | None = None
    destinationName: str | None = None

class BreakdownItem(BaseModel):
    label: str
    score: int = Field(ge=0, le=100)

class AIRoute(BaseModel):
    id: str
    name: Optional[str] = None
    routeType: str = "driving"
    safetyScore: int = Field(ge=0, le=100)
    summary: str = "No analysis available."
    accentColor: str = "#F59E0B"
    breakdown: List[BreakdownItem] = []

# DeepSeek JSON mode requires the root to be an OBJECT, not a bare array,
# so wrap the list in a key.
class AIRouteList(BaseModel):
    routes: List[AIRoute]
    
@app.get("/")
def root():
    return {"message": "Welcome to SafePath API"}


@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.get("/api/langflow/health")
def langflow_health():
    return {
        "status": "ok",
        "langflow_target": LANGFLOW_URL,
        "auth_configured": bool(LANGFLOW_API_KEY)
    }


# ---------------------------------------------------------------------------
# Langfuse monitoring (read-only) — pulls traces/observations via the SDK.
# ---------------------------------------------------------------------------
@app.get("/api/monitor/health")
def monitor_health():
    """Check the backend can reach Langfuse with valid credentials."""
    try:
        return langfuse_monitor.ping()
    except langfuse_monitor.LangfuseConfigError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Langfuse unreachable: {exc}")


@app.get("/api/monitor/traces")
def monitor_traces(minutes: int = 60, limit: int = 50, include_io: bool = False):
    """Recent traces (summarised), newest first.

    Pass include_io=true to add truncated input/output previews.
    """
    try:
        return {
            "traces": langfuse_monitor.fetch_recent_traces(
                minutes=minutes, limit=limit, include_io=include_io
            )
        }
    except langfuse_monitor.LangfuseConfigError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Langfuse query failed: {exc}")


@app.get("/api/monitor/traces/{trace_id}")
def monitor_trace_detail(trace_id: str):
    """Full detail for one trace: complete input/output + all observations."""
    try:
        return langfuse_monitor.fetch_trace_detail(trace_id)
    except langfuse_monitor.LangfuseConfigError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Langfuse query failed: {exc}")


@app.get("/api/monitor/alerts")
def monitor_alerts(
    minutes: int = 60,
    latency_threshold: float = langfuse_monitor.DEFAULT_LATENCY_THRESHOLD_S,
    limit: int = 100,
    check_errors: bool = True,
):
    """High-latency and error/warning alerts from recent traces."""
    try:
        return langfuse_monitor.build_alerts(
            minutes=minutes,
            latency_threshold_s=latency_threshold,
            limit=limit,
            check_errors=check_errors,
        )
    except langfuse_monitor.LangfuseConfigError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Langfuse query failed: {exc}")


@app.get("/api/monitor/stats")
def monitor_stats(minutes: int = 1440, limit: int = 500):
    """Aggregate volume / latency / cost / per-user stats (default last 24h)."""
    try:
        return langfuse_monitor.build_stats(minutes=minutes, limit=limit)
    except langfuse_monitor.LangfuseConfigError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Langfuse query failed: {exc}")

@app.get("/api/monitor/export")
def monitor_export(
    minutes: int = 1440,
    limit: int = 1000,
    format: str = "csv",
    include_io: bool = True,
):
    """Download recent traces as a downloadable CSV or JSON file.

    Query params:
      minutes     time window to pull (default 1440 = last 24h)
      limit       max traces (default 1000)
      format      "csv" (default) or "json"
      include_io  attach truncated input/output previews (default true)

    Example:
      /api/monitor/export?minutes=10080&format=csv   # last 7 days as CSV
    """
    try:
        traces = langfuse_monitor.fetch_recent_traces(
            minutes=minutes, limit=limit, include_io=include_io
        )
    except langfuse_monitor.LangfuseConfigError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Langfuse query failed: {exc}")

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")

    if format.lower() == "json":
        payload = json.dumps({"traces": traces}, ensure_ascii=False, indent=2)
        return Response(
            content=payload,
            media_type="application/json",
            headers={
                "Content-Disposition": f'attachment; filename="langfuse-traces-{stamp}.json"'
            },
        )

    # Default: CSV. csv.DictWriter handles quoting of commas/newlines safely.
    fieldnames = [
        "id", "name", "timestamp", "user_id", "session_id",
        "latency_s", "total_cost", "tags", "url",
        "input_preview", "output_preview",
    ]
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    for t in traces:
        row = dict(t)
        if isinstance(row.get("tags"), list):
            row["tags"] = ", ".join(map(str, row["tags"]))
        writer.writerow(row)

    return Response(
        content=buf.getvalue(),
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="langfuse-traces-{stamp}.csv"'
        },
    )

# ---------------------------------------------------------------------------
# Admin — user route-search logs (read-only, sourced from Langfuse).
# Powers SafePathAdminSearchLogsView.vue (replaces its hard-coded mock array).
# ---------------------------------------------------------------------------
@app.get("/api/admin/search-logs")
def admin_search_logs(minutes: int = 1440, limit: int = 100):
    """Recent user route searches, newest first (default: last 24h).

    Each row: user (masked), start, destination, date, time, safetyScore,
    status — the exact shape the admin "User Search Logs" table renders.
    """
    try:
        return {
            "logs": langfuse_search_logs.fetch_search_logs(
                minutes=minutes, limit=limit
            )
        }
    except langfuse_monitor.LangfuseConfigError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Langfuse query failed: {exc}")


'''
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

@app.get("/api/places")
def search_places(query: str):
    """
    Search for locations by name using LocationIQ's Autocomplete API
    (built on Nominatim/OSM data, but keyed instead of IP-based —
    avoids the 403 blocks from free anonymous demo servers).
    """
    if not query or len(query) < 3:
        return {"places": []}

    url = "https://api.locationiq.com/v1/autocomplete"

    params = {
        "key": LOCATIONIQ_API_KEY,
        "q": query,
        "format": "json",
        "limit": 5,
        "countrycodes": "de",
        "viewbox": "13.0883,52.3383,13.7611,52.6755",
        "bounded": 1,
        "normalizeaddress": 1,
    }

    try:
        resp = httpx.get(url, params=params, timeout=10.0)
        resp.raise_for_status()
        data = resp.json()
    except httpx.HTTPStatusError as exc:
        # LocationIQ returns 404 with a JSON body when there are simply no results
        if exc.response.status_code == 404:
            return {"places": []}
        raise HTTPException(status_code=502, detail=f"Geocoding service error: {exc}")
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"Geocoding service error: {exc}")

    places = []
    for item in data:
        address = item.get("address") or {}

        name = (
            address.get("name")
            or item.get("display_place")
            or address.get("road")
            or item.get("display_name")
        )

        subtitle_parts = [
            address.get("suburb") or address.get("city_district"),
            address.get("city") or address.get("town"),
        ]
        subtitle = ", ".join(p for p in subtitle_parts if p)

        places.append({
            "name": name,
            "subtitle": subtitle,
            "display_name": item.get("display_name"),
            "lat": float(item["lat"]),
            "lng": float(item["lon"]),
        })

    return {"places": places}


def log_route_search_trace(
    *,
    guest_id: str,
    session_id: str,
    start_name: str | None,
    dest_name: str | None,
    start_coords: str,
    dest_coords: str,
    route_suggestions: list[dict],
    ai_ok: bool,
    duration_s: float,
) -> None:
    """Record one route search as a Langfuse trace ("safepath-route-search").

    Written directly from the backend with the Langfuse SDK, so tracing does
    NOT depend on Langflow or the LiteLLM proxy forwarding anything. This is
    the source the admin search-logs endpoint reads back. Best-effort: any
    failure is logged and swallowed so a user's route request never breaks.
    """
    try:
        client = langfuse_monitor.get_client()
    except langfuse_monitor.LangfuseConfigError:
        return  # credentials not configured — skip tracing silently

    try:
        start_label = start_name or start_coords
        dest_label = dest_name or dest_coords
        best_score = max(
            (r.get("safetyScore", 0) for r in route_suggestions), default=0
        )
        trace_input = {"start": start_label, "destination": dest_label}
        trace_metadata = {
            "startName": start_name or "",
            "destinationName": dest_name or "",
            "start_coords": start_coords,
            "destination_coords": dest_coords,
        }
        trace_output = {
            "status": "Success" if route_suggestions else "Failed",
            "aiScored": ai_ok,
            "routeCount": len(route_suggestions),
            "bestSafetyScore": best_score,
            "durationSeconds": round(duration_s, 2),
            "routes": [
                {
                    "id": r.get("id"),
                    "safetyScore": r.get("safetyScore"),
                    "distance": r.get("distance"),
                    "duration": r.get("duration"),
                    "summary": r.get("summary"),
                    "breakdown": r.get("breakdown", []),
                }
                for r in route_suggestions
            ],
        }

        with client.start_as_current_span(
            name="safepath-route-search", input=trace_input
        ) as span:
            span.update_trace(
                name="safepath-route-search",
                user_id=guest_id,
                session_id=session_id,
                tags=["route-search"],
                input=trace_input,
                output=trace_output,
                metadata=trace_metadata,
            )
        # No blocking flush() here: the SDK exports in the background so we
        # don't stall the async request. Traces flush on interval / shutdown.
    except Exception as exc:  # never let tracing break routing
        print(f"[LANGFUSE] route-search trace failed: {exc}")


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
    f"[TIME] {routes.__len__()} Route processing: "
    f"{process_routes_end - process_routes_start:.2f} sec"
)
    # ---------------------------------------------------
    # STEP 2: AI SAFETY ANALYSIS
    # ---------------------------------------------------

    # Prompt is managed in Langfuse ("safepath-route-safety"). Fetched and
    # compiled at request time; falls back to FALLBACK_ROUTE_PROMPT if
    # Langfuse is unreachable so routing never breaks.
    prompt = langfuse_prompts.get_compiled_prompt(
        langfuse_prompts.ROUTE_SAFETY_PROMPT,
        {
            "from_lat": s.lat,
            "from_lng": s.lng,
            "to_lat": d.lat,
            "to_lng": d.lng,
            "routes_json": json.dumps(llm_summaries, indent=2),
        },
        fallback=FALLBACK_ROUTE_PROMPT,
    )
    print("Prompt for AI scoring:\n", prompt)
    print("Start Name:", req.startName, "Destination Name:", req.destinationName)

    langflow_payload = {
        "input_value": prompt,
        "output_type": "chat",
        "input_type": "chat",
    }
    # Langflow 1.9.2's run endpoint only forwards `session_id` to Langfuse (it
    # ignores `user_id`), and Langflow stamps its own account id as the trace
    # user_id. So we track the visitor via the SESSION ID instead: we embed the
    # guest id inside a per-flow-namespaced session id (below). `user_id` is sent
    # too, harmlessly, in case a future Langflow/flow component starts using it.
    if req.user_id:
        langflow_payload["user_id"] = req.user_id
    # Route session_id = "route_<guest id>_<per-request id>". The guest id keeps
    # the request tied to the visitor (filter Session ID in TEXT mode by it); the
    # "route_" prefix + per-request suffix make every route call its own isolated
    # session, so it never shares an Agent-memory bucket with the chat flow
    # ("chat_...") or with the user's other route requests — which is what
    # prevents the cross-flow / cross-request hallucination bleed.
    guest_id = req.user_id or req.session_id or f"guest_{uuid.uuid4()}"
    route_session_id = f"route_{guest_id}_{uuid.uuid4()}"
    langflow_payload["session_id"] = route_session_id
    print("UserId:",guest_id)
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
    langflow_start = time.perf_counter()
    ai_routes = await score_routes_with_ai(prompt)
    print(f"[TIME] AI scoring: {time.perf_counter() - langflow_start:.2f} sec")
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

    # Trace this route search in Langfuse (best-effort; never breaks routing).
    # This is the single source of truth for the admin "User Search Logs".
    log_route_search_trace(
        guest_id=guest_id,
        session_id=route_session_id,
        start_name=req.startName,
        dest_name=req.destinationName,
        start_coords=f"{s.lat:.5f}, {s.lng:.5f}",
        dest_coords=f"{d.lat:.5f}, {d.lng:.5f}",
        route_suggestions=route_suggestions,
        ai_ok=bool(ai_routes),
        duration_s=api_end - api_start,
    )

    return {
        "route_suggestions": route_suggestions
    }


async def score_routes_with_ai(prompt: str) -> list[dict]:
    messages = [{"role": "user", "content": prompt}]
    last_err = None

    for _ in range(2):  # initial try + one retry
        resp = await litellm_client.chat.completions.create(
            model="deepseek/deepseek-v3.2",
            messages=messages,
            response_format={"type": "json_object"},  # forces valid JSON
            max_tokens=2000,                           # high, so it never truncates
            temperature=0,                             # deterministic scoring
        )

        # Read CONTENT ONLY — never reasoning_content. This kills the Chinese leak.
        content = resp.choices[0].message.content or ""

        # Defensive: if the proxy ever merges reasoning in, drop everything
        # up to and including the last </think>.
        if "</think>" in content:
            content = content.rsplit("</think>", 1)[-1].strip()

        if not content:
            last_err = "empty content"
            messages.append({"role": "user",
                             "content": "You returned empty content. Return only the JSON object."})
            continue

        try:
            parsed = AIRouteList.model_validate_json(content)
            return [r.model_dump() for r in parsed.routes]
        except Exception as e:
            last_err = str(e)
            messages.append({"role": "assistant", "content": content})
            messages.append({"role": "user",
                             "content": f"Your last response was invalid: {e}. "
                                        "Return ONLY a JSON object matching the schema. "
                                        "All scores must be integers 0-100."})

    print("AI scoring failed:", last_err)
    print("Message:", messages)
    return []  # your existing fallback block then takes over