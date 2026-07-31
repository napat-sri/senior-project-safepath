"""Client for the safepath-mcp service (real crime / lighting / accident data).

`/api/routes/safe` used to ask the LLM to invent a safetyScore out of thin
air. This module instead calls the `get_routes_safety_context` tool exposed
by backend/mcp/mcp_server.py (SSE transport), which computes real numbers
from the Kriminalitätsatlas, Unfallatlas, and OpenStreetMap lighting data
already loaded into that service.

Fails soft: any connection or protocol error is logged and swallowed,
returning {} so a route search never breaks just because the MCP service is
down (main.py falls back to neutral scores in that case, same spirit as the
existing Langflow/AI fallback).
"""

from __future__ import annotations

import json
import os

from mcp import ClientSession
from mcp.client.sse import sse_client

# "mcp" is the service name in docker-compose(.dev).yml; 8000/sse is
# FastMCP's default SSE transport endpoint. Override via env if needed.
MCP_SSE_URL = os.getenv("MCP_SSE_URL", "http://mcp:8000/sse")

TOOL_GET_ROUTES_SAFETY_CONTEXT = "get_routes_safety_context"


async def get_routes_safety_context(routes: list[dict], sample_every_m: int = 300) -> dict:
    """Fetch real crime/lighting/accident scores for one or more routes.

    routes: [{"id": "route-1", "coordinates": [[lat, lng], ...]}, ...]

    Returns a dict keyed by route id:
        {"route-1": {"sample_count": int,
                     "avg_crime_safety_score": int | None,
                     "avg_lighting_safety_score": int | None,
                     "avg_accident_safety_score": int | None}, ...}
    or {} if the MCP service could not be reached / returned an error.
    """
    if not routes:
        return {}

    try:
        async with sse_client(MCP_SSE_URL, timeout=10.0, sse_read_timeout=30.0) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(
                    TOOL_GET_ROUTES_SAFETY_CONTEXT,
                    {"routes": routes, "sample_every_m": sample_every_m},
                )

        if result.isError:
            print(f"[MCP] {TOOL_GET_ROUTES_SAFETY_CONTEXT} returned an error: {result.content}")
            return {}

        # The tool is annotated `-> dict`, so FastMCP ships it as unstructured
        # text content (JSON-encoded), not structuredContent. Handle both so
        # this keeps working if the tool's return annotation ever changes.
        if result.structuredContent is not None:
            data = result.structuredContent
            if isinstance(data, dict) and set(data.keys()) == {"result"}:
                data = data["result"]
            return data

        if result.content:
            text = getattr(result.content[0], "text", None)
            if text:
                return json.loads(text)

        return {}
    except Exception as exc:  # noqa: BLE001 -- never let MCP downtime break routing
        print(f"[MCP] {TOOL_GET_ROUTES_SAFETY_CONTEXT} call failed: {exc}")
        return {}
