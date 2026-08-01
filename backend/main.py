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
    
    Admin endpoints (Keycloak user management, Admin role required):
    Get    /api/admin/users                 :list/search Keycloak users (paginated).
    Post   /api/admin/users                 :create a new Keycloak user.
    Put    /api/admin/users/{user_id}       :update a user's name/email/role.
    Delete /api/admin/users/{user_id}       :delete a Keycloak user.

    SafePath routing endpoints:
    Get /api/places :search for locations by name using LocationIQ's Autocomplete API.
    Get /api/routes/safe :fetch safe routes between two points, scored by AI for safety.
    

"""

import csv
import io
import json
import os
import time
import uuid
from datetime import datetime, timezone

import httpx
import langfuse_monitor
import langfuse_prompts
import langfuse_search_logs
import mcp_client
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from openai import AsyncOpenAI
from pydantic import BaseModel, Field
from typing import Literal

LITELLM_PROXY_URL = os.getenv("LITELLM_PROXY_URL")# default for local dev
LITELLM_VIRTUAL_KEY = os.getenv("LITELLM_VIRTUAL_KEY")# default for local dev
litellm_client = AsyncOpenAI(
    base_url=LITELLM_PROXY_URL,    
    api_key=LITELLM_VIRTUAL_KEY,  
)

import keycloak_admin
from datetime import date
from sqlalchemy import select, desc
from sqlalchemy.orm import Session
from database import IncidentReport, init_db, get_db, UserProfile
from auth import require_admin, require_member

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

# Driving: public OSRM demo server (car dataset).
# Walking: self-hosted OSRM with the foot.lua profile (see docker-compose.dev.yml
# `osrm-foot` / `osrm-foot-import`) — the public demo server's /route/v1/foot/
# path does NOT have a real foot dataset. Verified: querying the same two
# points against /driving/ and /foot/ on the public server returns byte-identical
# distance/duration, i.e. "foot" silently falls back to driving-speed results
# instead of erroring, which would give wrong walking times/routes if used.
OSRM_DRIVING_URL = os.getenv("OSRM_DRIVING_URL", "https://router.project-osrm.org/route/v1/driving")
OSRM_WALKING_URL = os.getenv("OSRM_WALKING_URL", "http://osrm-foot:5000/route/v1/foot")
OSRM_PROFILE_URLS = {"driving": OSRM_DRIVING_URL, "walking": OSRM_WALKING_URL}
FLOW_ID = os.getenv("VUE_APP_LANGFLOW_ROUTE_AGENT_FLOW_ID")
LANGFLOW_URL = f"http://langflow:7860/api/v1/run/{FLOW_ID}" 
# Authentication Key for Langflow (Required if login is enabled in the Langflow UI)
LANGFLOW_API_KEY = os.getenv("VUE_APP_LANGFLOW_API_KEY")
# LocationIQ API Key for geocoding (autocomplete) requests. Required.
LOCATIONIQ_API_KEY = os.getenv("LOCATIONIQ_API_KEY")


# ---------------------------------------------------------------------------
# Route-safety scoring weights.
#
# safetyScore itself is now computed deterministically in Python from real
# data (see compute_safety_score below) — crime + accident history from the
# Kriminalitätsatlas/Unfallatlas and street-lighting density from OpenStreetMap,
# served by the safepath-mcp service (backend/mcp/mcp_server.py) and fetched
# via mcp_client.get_routes_safety_context. The LLM is no longer asked to
# invent numeric scores; it only writes the human-readable name/summary,
# grounded in the real numbers we hand it.
# ---------------------------------------------------------------------------
SAFETY_WEIGHTS = {"accident": 0.35, "crime": 0.35, "lighting": 0.30}
DEFAULT_SUBSCORE = 50  # neutral fallback when a data source has no coverage for a route

# ---------------------------------------------------------------------------
# Route-summary prompt fallback.
#
# The live prompt is managed in Langfuse under the name
# `safepath-route-safety` and fetched at request time (see langfuse_prompts).
# This string is the exact same text and is used only if Langfuse is
# unreachable, so routing keeps working. Keep the two copies in sync — this
# was reworked to consume real scores rather than invent them, so update the
# Langfuse UI prompt to match if you change this.
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

ROUTES (each already has real safetyScore + accident/crime/lighting sub-scores,
computed from Berlin crime, accident, and street-lighting data — do NOT change
or re-derive these numbers, just explain them):
{{routes_json}}

For each route, write only "name" and "summary":
- name: a short human-friendly route name (e.g. "Route 1" or a street-based name).
- summary: two sentences referencing the ALREADY-GIVEN safetyScore/sub-scores —
  why this route ranks where it does, and one trade-off vs the other routes.

Rules:
- Never use placeholders, dashes (---), dots (.), null, or blanks. Every field must have a real value.
- Return one object per route in the ROUTES input, keeping the same "id".
- Do NOT include safetyScore, breakdown, or accentColor in your output — those are supplied separately.

Example of the exact format (values illustrative only):
[
  {
    "id": "route-1",
    "name": "Route 1",
    "summary": "This route has the highest safety score thanks to well-lit main streets and low crime along the way, though it's slightly longer than the alternative."
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
    # "walking" (self-hosted OSRM foot profile) or "driving" (public OSRM
    # demo server). Defaults to walking — this is a pedestrian safety app.
    travelMode: Literal["driving", "walking"] = "walking"

class BreakdownItem(BaseModel):
    label: str
    score: int = Field(ge=0, le=100)

# The AI only supplies narrative fields now — safetyScore/breakdown/accentColor
# are computed deterministically from real MCP data (compute_safety_score).
class AIRoute(BaseModel):
    id: str
    name: str | None = None
    summary: str = "No analysis available."

# DeepSeek JSON mode requires the root to be an OBJECT, not a bare array,
# so wrap the list in a key.
class AIRouteList(BaseModel):
    routes: list[AIRoute]
    
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
    except Exception as exc:  # noqa: BLE001 -- intentional catch-all, converted to an HTTP error response
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
    except Exception as exc:  # noqa: BLE001 -- intentional catch-all, converted to an HTTP error response
        raise HTTPException(status_code=502, detail=f"Langfuse query failed: {exc}")


@app.get("/api/monitor/traces/{trace_id}")
def monitor_trace_detail(trace_id: str):
    """Full detail for one trace: complete input/output + all observations."""
    try:
        return langfuse_monitor.fetch_trace_detail(trace_id)
    except langfuse_monitor.LangfuseConfigError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    except Exception as exc:  # noqa: BLE001 -- intentional catch-all, converted to an HTTP error response
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
    except Exception as exc:  # noqa: BLE001 -- intentional catch-all, converted to an HTTP error response
        raise HTTPException(status_code=502, detail=f"Langfuse query failed: {exc}")


@app.get("/api/monitor/stats")
def monitor_stats(minutes: int = 1440, limit: int = 500):
    """Aggregate volume / latency / cost / per-user stats (default last 24h)."""
    try:
        return langfuse_monitor.build_stats(minutes=minutes, limit=limit)
    except langfuse_monitor.LangfuseConfigError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    except Exception as exc:  # noqa: BLE001 -- intentional catch-all, converted to an HTTP error response
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
    except Exception as exc:  # noqa: BLE001 -- intentional catch-all, converted to an HTTP error response
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
    except Exception as exc:  # noqa: BLE001 -- intentional catch-all, converted to an HTTP error response
        raise HTTPException(status_code=502, detail=f"Langfuse query failed: {exc}")


# ---------------------------------------------------------------------------
# Admin — Keycloak user management (read/write).
# Powers SafePathAdminUserManagement.vue (replaces its hard-coded mock array).
# All four routes require the caller's token to carry the Admin realm role.
# ---------------------------------------------------------------------------
class UserWriteRequest(BaseModel):
    name: str
    email: str
    role: str      # one of keycloak_admin.KNOWN_ROLES: "Admin" | "Member"

@app.get("/api/admin/users")
def admin_list_users(
    search: str = "", first: int = 0, max: int = 20,
    _admin=Depends(require_admin),          # noqa: B008
    db: Session = Depends(get_db),          # noqa: B008
):
    """One page of Keycloak users, matching `search` against name/username/email."""
    try:
        result = keycloak_admin.fetch_users(search=search, first=first, max=max)
        # Attach avatars stored in our Postgres, keyed by Keycloak id (= sub = row["id"]).
        ids = [row["id"] for row in result["users"]]
        if ids:
            rows = db.query(UserProfile).filter(UserProfile.user_id.in_(ids)).all()
            avatar_map = {p.user_id: p.avatar for p in rows}
            for row in result["users"]:
                row["avatar"] = avatar_map.get(row["id"])
        return result
    except keycloak_admin.KeycloakConfigError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=502, detail=f"Keycloak error: {exc}")
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"Keycloak unreachable: {exc}")


@app.post("/api/admin/users")
def admin_create_user(payload: UserWriteRequest, _admin=Depends(require_admin)):  # noqa: B008 -- FastAPI's Depends is meant to be used as a default value
    """Create a Keycloak user (Add User button). Sets a random temp password
    and forces a password reset on first login — see keycloak_admin.create_user."""
    try:
        return keycloak_admin.create_user(
            name=payload.name, email=payload.email, role=payload.role
        )
    except keycloak_admin.KeycloakConfigError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=502, detail=f"Keycloak error: {exc}")
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"Keycloak unreachable: {exc}")


@app.put("/api/admin/users/{user_id}")
def admin_update_user(user_id: str, payload: UserWriteRequest, _admin=Depends(require_admin)):  # noqa: B008 -- FastAPI's Depends is meant to be used as a default value
    try:
        return keycloak_admin.update_user(
            user_id, name=payload.name, email=payload.email, role=payload.role
        )
    except keycloak_admin.KeycloakConfigError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            raise HTTPException(status_code=404, detail="User not found.")
        raise HTTPException(status_code=502, detail=f"Keycloak error: {exc}")
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"Keycloak unreachable: {exc}")


@app.delete("/api/admin/users/{user_id}")
def admin_delete_user(user_id: str, _admin=Depends(require_admin)):  # noqa: B008 -- FastAPI's Depends is meant to be used as a default value
    """Permanently delete a Keycloak user (Delete button)."""
    try:
        keycloak_admin.delete_user(user_id)
        return {"deleted": True}
    except keycloak_admin.KeycloakConfigError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            raise HTTPException(status_code=404, detail="User not found.")
        raise HTTPException(status_code=502, detail=f"Keycloak error: {exc}")
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"Keycloak unreachable: {exc}")

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
    except Exception as exc:  # noqa: BLE001 -- never let tracing break routing
        print(f"[LANGFUSE] route-search trace failed: {exc}")


def accent_color_for(safety_score: int) -> str:
    if safety_score >= 85:
        return "#0B8043"
    if safety_score >= 70:
        return "#E8590C"
    return "#C1121F"


def compute_safety_score(ctx: dict | None) -> dict:
    """Turn one route's MCP safety context into safetyScore + breakdown + accentColor.

    ctx is the per-route dict from mcp_client.get_routes_safety_context (or
    None/missing if the MCP call failed or that route had no data). Missing
    sub-scores fall back to DEFAULT_SUBSCORE and are excluded from the
    weighted average's denominator (so one missing source doesn't drag the
    score toward 50 more than it should) — if every source is missing, the
    whole route falls back to a neutral 50.
    """
    ctx = ctx or {}
    subscores = {
        "accident": ctx.get("avg_accident_safety_score"),
        "crime": ctx.get("avg_crime_safety_score"),
        "lighting": ctx.get("avg_lighting_safety_score"),
    }
    available = {k: v for k, v in subscores.items() if v is not None}

    if available:
        total_weight = sum(SAFETY_WEIGHTS[k] for k in available)
        safety_score = round(
            sum(v * SAFETY_WEIGHTS[k] for k, v in available.items()) / total_weight
        )
    else:
        safety_score = DEFAULT_SUBSCORE

    # Labels use "X Safety" consistently — all three, like safetyScore itself,
    # are HIGHER = SAFER. ("Accident Risk" / "Crime Level" previously implied
    # the opposite direction — higher = more danger — which didn't match the
    # actual values and confused readers of the breakdown.)
    breakdown = [
        {"label": "Accident Safety", "score": subscores["accident"] if subscores["accident"] is not None else DEFAULT_SUBSCORE},
        {"label": "Crime Safety", "score": subscores["crime"] if subscores["crime"] is not None else DEFAULT_SUBSCORE},
        {"label": "Lighting Safety", "score": subscores["lighting"] if subscores["lighting"] is not None else DEFAULT_SUBSCORE},
    ]

    return {
        "safetyScore": safety_score,
        "breakdown": breakdown,
        "accentColor": accent_color_for(safety_score),
    }


@app.post("/api/routes/safe")
async def get_safe_routes(req: RouteRequest):
    api_start = time.perf_counter()
    """
    1. Fetches candidate routes from OSRM.
    2. Fetches real crime/accident/lighting data from the MCP server and computes
       each route's safetyScore deterministically (see compute_safety_score).
    3. Asks the LLM directly (LiteLLM, not Langflow) for a name/summary per route,
       grounded in those real scores.
    4. Returns each route's score, summary, and map coordinates to the frontend.
    """
    s, d = req.start, req.destination
    osrm_base_url = OSRM_PROFILE_URLS.get(req.travelMode, OSRM_PROFILE_URLS["walking"])
    osrm_url = f"{osrm_base_url}/{s.lng},{s.lat};{d.lng},{d.lat}"
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

    process_routes_end = time.perf_counter()
    print(
    f"[TIME] {routes.__len__()} Route processing: "
    f"{process_routes_end - process_routes_start:.2f} sec"
)
    # ---------------------------------------------------
    # STEP 2: REAL SAFETY DATA (crime, accident, street lighting) via MCP
    # ---------------------------------------------------
    # Calls the safepath-mcp service (backend/mcp/mcp_server.py) which serves
    # real Berlin crime/accident/lighting data — no LLM guessing involved.
    mcp_start = time.perf_counter()
    mcp_routes_payload = [
        {"id": route["id"], "coordinates": route["coordinates"]}
        for route in routes
    ]
    safety_context = await mcp_client.get_routes_safety_context(mcp_routes_payload)
    print(f"[TIME] MCP safety context: {time.perf_counter() - mcp_start:.2f} sec")
    if not safety_context:
        print("[MCP] No safety context returned — using neutral scores for all routes.")

    route_scores = {
        route["id"]: compute_safety_score(safety_context.get(route["id"]))
        for route in routes
    }

    # ---------------------------------------------------
    # STEP 3: AI NARRATIVE — name + summary only, grounded in the real scores
    # ---------------------------------------------------
    llm_summaries = [  # Send to Langflow/LLM: real numbers, not just distance/duration
        {
            "id": route["id"],
            "distance_km": round(route["distance_m"] / 1000, 1),
            "duration_min": round(route["duration_s"] / 60),
            "safetyScore": route_scores[route["id"]]["safetyScore"],
            "breakdown": route_scores[route["id"]]["breakdown"],
        }
        for route in routes
    ]

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

    # guest_id/route_session_id identify this search for Langfuse tracing
    # (log_route_search_trace below, via the Langfuse SDK directly). This
    # endpoint does not call Langflow — scoring and narrative are both done
    # in-process (MCP + LiteLLM) — so no Langflow payload/headers are needed
    # here. Route session_id = "route_<guest id>_<per-request id>": the guest
    # id keeps the request tied to the visitor, and the per-request suffix
    # keeps every route search its own isolated trace.
    guest_id = req.user_id or req.session_id or f"guest_{uuid.uuid4()}"
    route_session_id = f"route_{guest_id}_{uuid.uuid4()}"
    print("UserId:", guest_id)

    ai_routes = []
    langflow_start = time.perf_counter()
    ai_routes = await score_routes_with_ai(prompt)
    print(f"[TIME] AI scoring: {time.perf_counter() - langflow_start:.2f} sec")
    ai_lookup = {ai_route.get("id"): ai_route for ai_route in ai_routes}

    # ---------------------------------------------------
    # STEP 4: BUILD RESPONSE — real scores always; AI only supplies narrative
    # ---------------------------------------------------
    # Unlike before, this no longer depends on the AI call succeeding: the
    # safetyScore/breakdown/accentColor below always come from real MCP data.
    # If the AI is unavailable, routes still get correct scores, just with a
    # generic summary sentence instead of a tailored one.
    route_suggestions = []
    merge_start = time.perf_counter()
    for i, route in enumerate(routes):
        route_id = route["id"]
        scores = route_scores[route_id]
        ai_route = ai_lookup.get(route_id, {})

        route_suggestions.append({
            "id": route_id,
            "name": ai_route.get("name") or f"Route {i + 1}",
            "origin": f"{s.lat:.4f}, {s.lng:.4f}",
            "destination": f"{d.lat:.4f}, {d.lng:.4f}",
            "routeType": req.travelMode,
            "safetyScore": scores["safetyScore"],
            "distance": route["distance"],
            "duration": route["duration"],
            "summary": ai_route.get("summary") or "Score based on real crime, accident, and street-lighting data for this route.",
            "accentColor": scores["accentColor"],
            "coordinates": route["coordinates"],
            "breakdown": scores["breakdown"],
        })
    merge_end = time.perf_counter()

    print(
        f"[TIME] Merge routes: "
        f"{merge_end - merge_start:.2f} sec"
    )
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
        except Exception as e:  # noqa: BLE001 -- intentional catch-all, converted to an HTTP error response
            last_err = str(e)
            messages.append({"role": "assistant", "content": content})
            messages.append({"role": "user",
                             "content": f"Your last response was invalid: {e}. "
                                        "Return ONLY a JSON object matching the schema. "
                                        "All scores must be integers 0-100."})

    print("AI scoring failed:", last_err)
    print("Message:", messages)
    return []  # your existing fallback block then takes over

@app.on_event("startup")
def _startup() -> None:
    init_db()

class IncidentCreate(BaseModel):
    reporterName: str | None = None
    incidentType: str
    location: str
    latitude: float | None = None
    longitude: float | None = None
    date: str          # "YYYY-MM-DD"
    time: str          # "HH:MM"
    details: str

class IncidentOut(BaseModel):
    id: int
    reporterName: str | None
    incidentType: str
    location: str
    latitude: float | None
    longitude: float | None
    date: str
    time: str
    details: str
    submittedBy: str | None
    createdAt: str

    @staticmethod
    def from_row(r: IncidentReport) -> "IncidentOut":
        return IncidentOut(
            id=r.id, reporterName=r.reporter_name, incidentType=r.incident_type,
            location=r.location, latitude=r.latitude, longitude=r.longitude,
            date=r.incident_date.isoformat(), time=r.incident_time,
            details=r.details,
            submittedBy=r.submitted_by, createdAt=r.created_at.isoformat(),
        )

# Member/Admin only: submit a report. Always records who submitted it.
@app.post("/api/incidents", response_model=IncidentOut)
def create_incident(
    payload: IncidentCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(require_member),
):
    row = IncidentReport(
        reporter_name=(payload.reporterName or "Anonymous"),
        incident_type=payload.incidentType,
        location=payload.location,
        latitude=payload.latitude,
        longitude=payload.longitude,
        incident_date=date.fromisoformat(payload.date),
        incident_time=payload.time,
        details=payload.details,
        submitted_by=(user.get("email") or user.get("preferred_username") or user.get("sub")),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return IncidentOut.from_row(row)

# Member/Admin only: recent reports for the form's "Recently Submitted Reports" panel.
@app.get("/api/incidents/recent")
def recent_incidents(
    limit: int = 10,
    db: Session = Depends(get_db),
    _member=Depends(require_member),
):
    rows = db.execute(
        select(IncidentReport).order_by(desc(IncidentReport.created_at)).limit(limit)
    ).scalars().all()
    return {"incidents": [IncidentOut.from_row(r).model_dump() for r in rows]}

# Admin only: full list for the admin table, newest first, optional status filter.
@app.get("/api/admin/incidents")
def admin_incidents(
    status: str | None = None, limit: int = 100,
    db: Session = Depends(get_db), _admin=Depends(require_admin),
):
    stmt = select(IncidentReport)
    if status and status != "All":
        stmt = stmt.where(IncidentReport.status == status)
    stmt = stmt.order_by(desc(IncidentReport.created_at)).limit(limit)
    rows = db.execute(stmt).scalars().all()
    return {"incidents": [IncidentOut.from_row(r).model_dump() for r in rows]}


# Fetch a single user
@app.get("/api/me")
def get_me(user=Depends(require_member)):
    """The caller's own profile — reads their Keycloak id from the verified token."""
    try:
        kc_user = keycloak_admin.fetch_user(user["sub"])
        return {"memberSince": kc_user.get("createdTimestamp")}  # epoch millis
    except keycloak_admin.KeycloakConfigError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=502, detail=f"Keycloak error: {exc}")
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"Keycloak unreachable: {exc}")

# Delete account permanently
@app.delete("/api/me")
def delete_me(user=Depends(require_member), db: Session = Depends(get_db)):  # noqa: B008
    """Delete the caller's own Keycloak account (id comes from the verified token)."""
    try:
        keycloak_admin.delete_user(user["sub"])
        profile = db.get(UserProfile, user["sub"])
        if profile is not None:
            db.delete(profile)
            db.commit()
        return {"deleted": True}
    except keycloak_admin.KeycloakConfigError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=502, detail=f"Keycloak error: {exc}")
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"Keycloak unreachable: {exc}")

class AvatarRequest(BaseModel):
    # Base64 data URL (e.g. "data:image/png;base64,..."). Send empty string to clear.
    avatar: str = Field("", max_length=500_000)

@app.get("/api/me/avatar")
def get_my_avatar(user=Depends(require_member), db: Session = Depends(get_db)):
    profile = db.get(UserProfile, user["sub"])
    return {"avatar": profile.avatar if profile else None}

@app.put("/api/me/avatar")
def set_my_avatar(payload: AvatarRequest, user=Depends(require_member), db: Session = Depends(get_db)):
    avatar = payload.avatar.strip()
    if avatar and not avatar.startswith((
        "data:image/png;base64,",
        "data:image/jpeg;base64,",
        "data:image/webp;base64,",
    )):
        raise HTTPException(status_code=422, detail="Avatar must be a base64 data URL (PNG/JPEG/WEBP).")

    profile = db.get(UserProfile, user["sub"])
    if profile is None:
        profile = UserProfile(user_id=user["sub"])
        db.add(profile)
    profile.avatar = avatar or None
    db.commit()
    return {"saved": True}