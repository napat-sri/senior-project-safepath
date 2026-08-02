"""Poll Keycloak login events into the durable safepath.login_events table."""
from __future__ import annotations

from datetime import datetime, timezone
from functools import lru_cache
from typing import Any

from sqlalchemy import select, func as safunc
from sqlalchemy.dialects.postgresql import insert as pg_insert

import keycloak_admin
from database import LoginEvent, SessionLocal

_EVENT_TYPES = ["LOGIN", "LOGIN_ERROR"]   # keep in sync with Keycloak "Saved types"


@lru_cache(maxsize=1024)
def _user_email(user_id: str) -> str | None:
    """Best-effort email for a Keycloak user id (cached; uses view-users)."""
    try:
        u = keycloak_admin._kc_request("GET", f"/users/{user_id}").json()
        return u.get("email")
    except Exception:
        return None


def _to_row(ev: dict[str, Any]) -> dict[str, Any]:
    details = ev.get("details") or {}
    ts = datetime.fromtimestamp((ev.get("time") or 0) / 1000, tz=timezone.utc)
    user_id = ev.get("userId")
    username = details.get("username")
    return {
        "event_time": ts,
        "type": ev.get("type", "LOGIN"),
        "user_id": user_id,
        "username": username,
        "email": (_user_email(user_id) if user_id else None) or username,
        "identity_provider": (details.get("identity_provider") or "Email").capitalize(),
        "client_id": ev.get("clientId"),
        "ip_address": ev.get("ipAddress"),
        "session_id": ev.get("sessionId"),
        "error": ev.get("error"),
        "dedup_key": "|".join([
            str(ev.get("time") or ""), ev.get("type", ""),
            user_id or username or "", ev.get("sessionId") or "", ev.get("ipAddress") or "",
        ]),
    }

def sync_login_events(max_events: int = 500) -> int:
    """Fetch recent Keycloak login events and upsert new ones. Returns #inserted."""
    db = SessionLocal()
    try:
        newest = db.execute(select(safunc.max(LoginEvent.event_time))).scalar()
        params: dict[str, Any] = {"first": 0, "max": max_events, "type": _EVENT_TYPES}
        if newest:
            params["dateFrom"] = newest.date().isoformat()   # date granularity; dedup handles overlap

        events = keycloak_admin._kc_request("GET", "/events", params=params).json()
        if not events:
            return 0

        rows = [_to_row(e) for e in events]
        stmt = pg_insert(LoginEvent).values(rows).on_conflict_do_nothing(
            index_elements=["dedup_key"]
        )
        result = db.execute(stmt)
        db.commit()
        return result.rowcount or 0
    finally:
        db.close()