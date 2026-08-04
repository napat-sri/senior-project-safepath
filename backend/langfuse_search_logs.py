"""SafePath admin — user route-search logs, sourced from Langfuse.

Turns the route-safety generations that the LiteLLM proxy logs to Langfuse
into the exact row shape the admin "User Search Logs" table expects, so the
frontend (SafePathAdminSearchLogsView.vue) can drop its hard-coded mock array
and read real data from ``GET /api/admin/search-logs``.

Row schema returned per log (matches the Vue table columns):

    id            trace id (also handy as a stable :key)
    user          masked guest / session id (no real auth on routing yet)
    userInitial   first character, for the avatar
    email         masked id (there is no real email on anonymous traces)
    start         origin place name (falls back to coordinates)
    destination   destination place name (falls back to coordinates)
    date          YYYY-MM-DD  (from the trace timestamp)
    time          HH:MM       (from the trace timestamp)
    safetyScore   best route's safety score parsed from the AI output (0-100)
    status        "Success" if the AI returned a score, else "Failed"
    sessionId     raw Langfuse session id (unmasked, for drill-down)
    url           clickable Langfuse trace link when available

Read-only. Reuses the cached Langfuse client + helpers from
``langfuse_monitor`` so we only ever build one client per process.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from typing import Any

# Reuse the single cached client + window helper + trace-url builder.
from langfuse_monitor import _trace_url, _window_start, get_client

# Tracking member's name and email
from functools import lru_cache
import keycloak_admin

# Traces the route flow stamps with this tag are definitely route searches.
ROUTE_TAG = "route-search"

# Metadata key spellings we accept for the origin / destination place names.
# Kept specific on purpose so we never grab an unrelated "start"/"to" field.
_START_NAME_KEYS = {"startname", "start_name", "origin_name", "originname"}
_DEST_NAME_KEYS = {"destinationname", "destination_name", "dest_name", "destname"}
_START_COORD_KEYS = {"start_coords", "startcoords", "origin_coords"}
_DEST_COORD_KEYS = {"destination_coords", "destinationcoords", "dest_coords"}

# A "lat, lng" pair, e.g. "52.5200, 13.4050" (used to read coords from input).
_COORD_PAIR = re.compile(r"-?\d{1,3}\.\d+\s*,\s*-?\d{1,3}\.\d+")
# Any safetyScore integer anywhere in the (stringified) AI output.
_SCORE_RE = re.compile(r'"safetyScore"\s*:\s*(\d{1,3})')


# --------------------------------------------------------------------------- #
# Small parsing helpers
# --------------------------------------------------------------------------- #
def _as_dict(value: Any) -> dict[str, Any]:
    """Coerce a metadata/output payload (dict, JSON string, or None) to a dict."""
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            return parsed if isinstance(parsed, dict) else {}
        except (json.JSONDecodeError, ValueError):
            return {}
    return {}


def _find_str(obj: Any, keyset: set[str]) -> str | None:
    """Depth-first search a nested dict/list for the first non-empty scalar
    whose key (case-insensitive) is in ``keyset``."""
    if isinstance(obj, dict):
        for key, val in obj.items():
            if (
                isinstance(key, str)
                and key.lower() in keyset
                and isinstance(val, (str, int, float))
                and str(val).strip()
            ):
                return str(val).strip()
        for val in obj.values():
            found = _find_str(val, keyset)
            if found:
                return found
    elif isinstance(obj, list):
        for val in obj:
            found = _find_str(val, keyset)
            if found:
                return found
    return None


def _coords_from_input(value: Any) -> tuple[str | None, str | None]:
    """Pull the first two 'lat, lng' pairs out of the trace input (the prompt).

    The route prompt embeds FROM/TO coordinates, so the first pair is the
    origin and the second is the destination. Used only as a fallback when
    metadata place names/coords are missing.
    """
    if value is None:
        return None, None
    text = value if isinstance(value, str) else json.dumps(value, default=str)
    pairs = _COORD_PAIR.findall(text)
    start = pairs[0].strip() if len(pairs) >= 1 else None
    dest = pairs[1].strip() if len(pairs) >= 2 else None
    return start, dest


def _extract_names(trace: Any) -> tuple[str, str]:
    """Best origin/destination labels: names → coords (metadata) → coords (input)."""
    meta = _as_dict(getattr(trace, "metadata", None))

    start = _find_str(meta, _START_NAME_KEYS) or _find_str(meta, _START_COORD_KEYS)
    dest = _find_str(meta, _DEST_NAME_KEYS) or _find_str(meta, _DEST_COORD_KEYS)

    # The backend writes an explicit input dict {"start": ..., "destination": ...}.
    if not start or not dest:
        inp = _as_dict(getattr(trace, "input", None))
        start = start or _find_str(inp, {"start", "startname", "origin"})
        dest = dest or _find_str(inp, {"destination", "destinationname", "dest"})

    # Last resort: pull the coordinate pairs out of a text prompt input.
    if not start or not dest:
        in_start, in_dest = _coords_from_input(getattr(trace, "input", None))
        start = start or in_start
        dest = dest or in_dest

    return start or "Unknown", dest or "Unknown"


def _extract_safety_score(output: Any) -> int | None:
    """Highest safetyScore found in the AI output (the best/recommended route)."""
    if output is None:
        return None
    text = output if isinstance(output, str) else json.dumps(output, default=str)
    scores = [int(m) for m in _SCORE_RE.findall(text)]
    scores = [s for s in scores if 0 <= s <= 100]
    return max(scores) if scores else None


def _mask_user(uid: Any) -> tuple[str, str]:
    """Return a friendly (user_label, masked_email) for an anonymous id.

    Guest ids look like "guest_<uuid>" / "route_<guest>_<uuid>"; we strip the
    prefix and keep a short slug so rows stay distinguishable but not PII.
    """
    raw = str(uid or "anonymous")
    core = raw
    for prefix in ("route_", "chat_", "guest_"):
        if core.startswith(prefix):
            core = core[len(prefix):]
            break
    slug = re.sub(r"[^A-Za-z0-9]", "", core)[:36] or "guest"
    return f"Guest {slug}", f"{slug}…@guest"


def _split_datetime(ts: Any) -> tuple[str, str]:
    """Split a trace timestamp into ('YYYY-MM-DD', 'HH:MM')."""
    if isinstance(ts, datetime):
        return ts.strftime("%Y-%m-%d"), ts.strftime("%H:%M")
    text = str(ts) if ts is not None else ""
    # ISO-8601 like "2026-06-24T18:42:11Z" → grab date + HH:MM defensively.
    date = text[:10] if len(text) >= 10 else ""
    time_ = text[11:16] if len(text) >= 16 else ""
    return date, time_


def _is_route_trace(trace: Any) -> bool:
    """Is this trace a route search?

    The backend writes each route search as a trace tagged ``route-search``
    with the name ``safepath-route-search``. We match on either so unrelated
    traces (e.g. the chat flow) are never counted.
    """
    tags = getattr(trace, "tags", None) or []
    if ROUTE_TAG in tags:
        return True
    name = (getattr(trace, "name", "") or "").lower()
    return "route" in name


# --------------------------------------------------------------------------- #
# Public API (used by the /api/admin/search-logs endpoint)
# --------------------------------------------------------------------------- #
def _to_log(trace: Any) -> dict[str, Any]:
    """Map one Langfuse trace to a search-log row."""
    date, time_ = _split_datetime(getattr(trace, "timestamp", None))
    uid = getattr(trace, "user_id", None) or getattr(trace, "session_id", None)
    # user_label, masked_email = _mask_user(uid)
    start, destination = _extract_names(trace)
    score = _extract_safety_score(getattr(trace, "output", None))
    user_detail = _resolve_user(uid)
    
    return {
        "id": getattr(trace, "id", None),
        "uid": (str(uid or "").split("_", 1)[1] if "_" in str(uid or "") else str(uid or "")),
        "user_detail": user_detail,
        # "userInitial": (user_label.replace("Guest ", "")[:1] or "G").upper(),
        # "role": (uid.split("_"))[0].capitalize(),
        # "email": masked_email,
        "start": start,
        "destination": destination,
        "timestamp": date + " " + time_,
        "date": date,
        "time": time_,
        "safetyScore": score if score is not None else 0,
        "status": "Success" if score is not None else "Failed",
        "sessionId": getattr(trace, "session_id", None),
        "url": _trace_url(trace),
    }


def fetch_search_logs(minutes: int = 1440, limit: int = 100, name: str | None = None) -> list[dict[str, Any]]:
    """Return route-search logs from the last ``minutes`` (default 24h), newest first."""
    client = get_client()
    result = client.api.trace.list(
        from_timestamp=_window_start(minutes),
        limit=limit,
        order_by="timestamp.desc",
        name= name or "safepath-route-search",
    )
    traces = getattr(result, "data", []) or []
    return [_to_log(t) for t in traces if _is_route_trace(t)]


@lru_cache(maxsize=2048)
def _lookup_keycloak_user(sub: str) -> tuple[str | None, str | None]:
    """(display_name, email) for a Keycloak user id; (None, None) on any failure."""
    try:
        u = keycloak_admin._kc_request("GET", f"/users/{sub}").json()
        name = f"{u.get('firstName','')} {u.get('lastName','')}".strip() or u.get("username")
        return name, u.get("email")
    except Exception:
        return None, None

def _resolve_user(uid):
    raw = str(uid or "anonymous")
    if raw.startswith("member_"):
        sub = raw[len("member_"):]
        name, email = _lookup_keycloak_user(sub)
        if name or email:
            display = name or email or "Member"
            return {"user": display, "email": email or "", "role": "Member",
                    "userInitial": (display[:1] or "M").upper()}
        # lookup failed → fall through to masked
    label, masked = _mask_user(raw)          # existing helper
    return {"user": label, "email": masked, "role": "Guest",
            "userInitial": ("G").upper()}