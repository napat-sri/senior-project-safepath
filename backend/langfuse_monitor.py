"""Langfuse monitoring / alerts for SafePath.

Reads traces + observations from the self-hosted Langfuse instance using the
official Python SDK (v3) and surfaces simple monitoring signals:

  - recent traces (summarised)
  - alerts: high-latency traces and traces that contain error/warning events
  - aggregate stats (volume, avg latency, cost, per-user activity)

Auth is read from environment variables (set in the backend's .env):

  LANGFUSE_PUBLIC_KEY=pk-lf-...
  LANGFUSE_SECRET_KEY=sk-lf-...
  LANGFUSE_HOST=http://langfuse-web:3000        # internal (shared caddy net)
  # or: LANGFUSE_HOST=https://langfuse.safepath.duckdns.org   # public fallback

Nothing here writes to Langfuse; it is read-only.
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from typing import Any

from langfuse import Langfuse

# Default alert thresholds (overridable per-request via query params).
DEFAULT_LATENCY_THRESHOLD_S = 15.0   # a route analysis slower than this is flagged
ERROR_LEVELS = {"ERROR", "WARNING"}  # observation levels considered "alert-worthy"


class LangfuseConfigError(RuntimeError):
    """Raised when the Langfuse credentials are missing."""


@lru_cache(maxsize=1)
def get_client() -> Langfuse:
    """Return a cached Langfuse client built from environment variables."""
    public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
    secret_key = os.getenv("LANGFUSE_SECRET_KEY")
    host = os.getenv("LANGFUSE_HOST", "http://langfuse-web:3000")

    if not public_key or not secret_key:
        raise LangfuseConfigError(
            "LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY must be set in the "
            "backend environment (.env)."
        )

    return Langfuse(public_key=public_key, secret_key=secret_key, host=host)


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def _iso(value: Any) -> str | None:
    """Best-effort ISO-8601 string for a datetime-ish value."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)


def _trace_url(trace: Any) -> str | None:
    """Build a clickable Langfuse URL for a trace when possible."""
    host = os.getenv("LANGFUSE_HOST", "").rstrip("/")
    html_path = getattr(trace, "html_path", None)
    if host and html_path:
        return f"{host}{html_path}"
    return None


def _summarise_trace(trace: Any) -> dict[str, Any]:
    """Convert an SDK trace object into a small JSON-friendly dict."""
    return {
        "id": getattr(trace, "id", None),
        "name": getattr(trace, "name", None),
        "timestamp": _iso(getattr(trace, "timestamp", None)),
        "user_id": getattr(trace, "user_id", None),
        "session_id": getattr(trace, "session_id", None),
        "latency_s": getattr(trace, "latency", None),
        "total_cost": getattr(trace, "total_cost", None),
        "tags": getattr(trace, "tags", None) or [],
        "url": _trace_url(trace),
    }


def _window_start(minutes: int) -> datetime:
    return datetime.now(timezone.utc) - timedelta(minutes=minutes)


# --------------------------------------------------------------------------- #
# Public functions (used by the API endpoints)
# --------------------------------------------------------------------------- #
def ping() -> dict[str, Any]:
    """Confirm the backend can reach Langfuse and credentials are valid."""
    client = get_client()
    # A tiny list call is the cheapest way to validate auth + connectivity.
    client.api.trace.list(limit=1)
    return {"status": "ok", "host": os.getenv("LANGFUSE_HOST")}


def fetch_recent_traces(minutes: int = 60, limit: int = 50) -> list[dict[str, Any]]:
    """Return summarised traces from the last `minutes`, newest first."""
    client = get_client()
    result = client.api.trace.list(
        from_timestamp=_window_start(minutes),
        limit=limit,
        order_by="timestamp.desc",
    )
    data = getattr(result, "data", []) or []
    return [_summarise_trace(t) for t in data]


def _trace_error_events(trace_id: str, max_events: int = 50) -> list[dict[str, Any]]:
    """Return error/warning observations belonging to a trace."""
    client = get_client()
    obs_result = client.api.observations.get_many(trace_id=trace_id, limit=max_events)
    observations = getattr(obs_result, "data", []) or []

    events: list[dict[str, Any]] = []
    for obs in observations:
        level = (getattr(obs, "level", "") or "").upper()
        if level in ERROR_LEVELS:
            events.append(
                {
                    "observation_id": getattr(obs, "id", None),
                    "name": getattr(obs, "name", None),
                    "level": level,
                    "status_message": getattr(obs, "status_message", None),
                }
            )
    return events


def build_alerts(
    minutes: int = 60,
    latency_threshold_s: float = DEFAULT_LATENCY_THRESHOLD_S,
    limit: int = 100,
    check_errors: bool = True,
) -> dict[str, Any]:
    """Scan recent traces and return alerts.

    Two alert types:
      - "high_latency": trace latency exceeds the threshold.
      - "error": trace contains an ERROR/WARNING observation.
    """
    client = get_client()
    result = client.api.trace.list(
        from_timestamp=_window_start(minutes),
        limit=limit,
        order_by="timestamp.desc",
    )
    traces = getattr(result, "data", []) or []

    alerts: list[dict[str, Any]] = []
    for trace in traces:
        summary = _summarise_trace(trace)

        latency = summary.get("latency_s")
        if latency is not None and latency > latency_threshold_s:
            alerts.append(
                {
                    "type": "high_latency",
                    "severity": "warning",
                    "message": f"Trace latency {latency:.1f}s exceeds "
                    f"{latency_threshold_s:.0f}s threshold.",
                    "trace": summary,
                }
            )

        if check_errors:
            for event in _trace_error_events(summary["id"]):
                alerts.append(
                    {
                        "type": "error",
                        "severity": "error" if event["level"] == "ERROR" else "warning",
                        "message": event["status_message"]
                        or f"{event['level']} in observation '{event['name']}'.",
                        "trace": summary,
                        "event": event,
                    }
                )

    return {
        "window_minutes": minutes,
        "latency_threshold_s": latency_threshold_s,
        "traces_scanned": len(traces),
        "alert_count": len(alerts),
        "alerts": alerts,
    }


def build_stats(minutes: int = 1440, limit: int = 500) -> dict[str, Any]:
    """Aggregate simple metrics over recent traces (default: last 24h)."""
    client = get_client()
    result = client.api.trace.list(
        from_timestamp=_window_start(minutes),
        limit=limit,
        order_by="timestamp.desc",
    )
    traces = getattr(result, "data", []) or []

    latencies = [
        getattr(t, "latency", None) for t in traces if getattr(t, "latency", None) is not None
    ]
    total_cost = sum(
        (getattr(t, "total_cost", 0) or 0) for t in traces
    )

    per_user: dict[str, int] = {}
    for t in traces:
        uid = getattr(t, "user_id", None) or "anonymous"
        per_user[uid] = per_user.get(uid, 0) + 1

    return {
        "window_minutes": minutes,
        "trace_count": len(traces),
        "avg_latency_s": round(sum(latencies) / len(latencies), 2) if latencies else None,
        "max_latency_s": round(max(latencies), 2) if latencies else None,
        "total_cost": round(total_cost, 6),
        "unique_users": len(per_user),
        "traces_per_user": dict(sorted(per_user.items(), key=lambda kv: kv[1], reverse=True)),
    }
