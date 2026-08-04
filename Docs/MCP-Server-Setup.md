# MCP Server Setup

How SafePath Berlin gets real crime/lighting/accident data into route scoring, instead of asking an LLM to guess a safety number. For the scoring formulas and calibration history, see `Docs/SafetyScoreMethodology.md` — this doc covers the MCP service itself: what it is, how it's called, and how it's deployed.

## Why it exists

`/api/routes/safe` originally asked an LLM (via Langflow) to invent a `safetyScore` from scratch. It had no real data — it was guessing. The MCP (Model Context Protocol) server fixes that: it's a small Python service that loads real Berlin datasets once at startup and exposes them as callable tools, so any score the backend produces is traceable back to an actual number in an actual dataset.

## Architecture

```
frontend --> backend (main.py) --> OSRM (routes)
                    |
                    v
              mcp_client.py --(SSE)--> mcp_server.py --> crime_lookup.py
                    |                                     lighting_lookup.py
                    v                                     accident_lookup.py
           compute_safety_score()  (deterministic, in main.py)
                    |
                    v
           LiteLLM (name + summary text only, not the score)
```

- **`backend/mcp/mcp_server.py`** — the MCP server. Loads the crime table, region polygons, and accident dataset once at import time, then exposes four tools over SSE transport on port 8000.
- **`backend/mcp/crime_lookup.py`**, **`lighting_lookup.py`**, **`accident_lookup.py`** — the three data sources, each a plain lookup module the server imports.
- **`backend/mcp_client.py`** — the backend-side client. Opens an SSE session to the MCP server and calls `get_routes_safety_context` for every request to `/api/routes/safe`.
- **`backend/main.py`** — orchestrates the whole request: fetches routes from OSRM, calls the MCP client for real data, computes `safetyScore` deterministically in `compute_safety_score()`, and only then asks the LLM (LiteLLM directly, not Langflow) to write a `name`/`summary` grounded in that already-computed score.

The key design point: the MCP server never talks to an LLM, and the LLM never sees raw data or computes a score. Scoring is deterministic Python; the LLM's only job is narrative text.

## Tools exposed by the MCP server

| Tool | Input | Returns |
|---|---|---|
| `get_crime_data(lat, lng)` | one coordinate | region name, crimes/km², `crime_safety_score` (0-100) |
| `get_lighting_density(lat, lng, radius_m=150)` | one coordinate | lamp count, lamps/km², `lighting_safety_score` |
| `get_accident_risk(lat, lng, radius_m=150)` | one coordinate | accident count, severity-weighted risk points, `accident_safety_score` |
| `get_routes_safety_context(routes, sample_every_m=300)` | **multiple** routes at once: `[{"id", "coordinates": [[lat,lng],...]}, ...]` | per-route averages of all three scores |

`get_routes_safety_context` is the one actually used in production — it samples each route's polyline every 300m and batches every route alternative into a single call, which is what keeps latency down (one round trip instead of one per sample point per route). The older single-route tool (`get_route_safety_context`) is left in the file, commented out, for reference.

## The three data sources

Briefly (full detail and calibration history in `Docs/SafetyScoreMethodology.md`):

1. **Crime** — Berlin police "Fallzahlen & HZ" spreadsheet, matched to a point via Bezirksregion polygons. Scored by crimes per km² (not the official cases-per-100k-residents rate, which badly distorted low-resident/high-foot-traffic areas like Alexanderplatz).
2. **Lighting** — a pre-fetched, in-memory dataset of 101,780 OpenStreetMap street-lamp nodes for Berlin (`backend/mcp/data/berlin_street_lamps.json`). Originally queried live from the Overpass API per-request; moved to a one-time bulk fetch after live queries proved flaky (406/504/429 errors) and added latency.
3. **Accidents** — Unfallatlas (German national accident atlas), 2021-2025 combined, 61,694 Berlin records, severity-weighted.

## Docker setup

The `mcp` service reuses the same image as `backend` (no separate Dockerfile or requirements.txt) — it just runs a different command against a different working directory. Dependencies for both live in one shared `backend/requirements.txt`, with `mcp[cli]` pinned below 2.0 (2.0 renamed `FastMCP` and dropped the `host`/`port`/`transport_security` constructor args this server relies on).

**Dev** (`docker-compose.dev.yml`):
```yaml
mcp:
  build: ./backend
  working_dir: /app/mcp
  command: ["python", "mcp_server.py"]
  volumes:
    - ./backend:/app
  networks:
    - langflow-net   # must share a network with `backend` so it can resolve "mcp"
```

**Production** (`docker-compose.yml`):
```yaml
mcp:
  build: ./backend
  working_dir: /app/mcp
  command: ["python", "mcp_server.py"]
  volumes:
    - /opt/apps/senior-project-safepath/backend:/app
  networks:
    - caddy
  depends_on:
    - backend
```

### Gotcha: build context vs. volume path must resolve differently

Production deploys run `docker compose` from *inside* a webhook container that has the Docker socket mounted (to control the real host's daemon) and its own bind mount (`/opt/apps/senior-project-safepath` -> `/app` inside itself). That split matters for this one service:

- **`build.context` stays relative** (`./backend`) — the compose CLI reads build files client-side, i.e. from inside the webhook container, where `./backend` correctly resolves to `/app/backend`.
- **`volumes:` must be absolute** (`/opt/apps/senior-project-safepath/backend:/app`) — bind mounts are resolved daemon-side, on the real host, which has no `/app` at all. A relative path here silently resolves against the webhook container's view, and Docker's `create_host_path: true` then creates an *empty* directory on the real host and mounts that instead of the real `backend/` folder — which looks like "the file exists (`ls` from inside the container confirms it) but the running container still can't find it."

If this deploy path ever changes, the volume line is the one to update — the build line should stay relative.

### Transport security

`FastMCP` auto-enables DNS-rebinding protection when `host` isn't explicitly set to something outside `127.0.0.1`/`localhost`. Since containers call this service by service name (`mcp`, or `safepath-mcp` if a compose file ever renames it), `mcp_server.py` sets `host="0.0.0.0"` explicitly and lists every hostname/origin the containers might use:

```python
security = TransportSecuritySettings(
    enable_dns_rebinding_protection=True,
    allowed_hosts=["mcp:8000", "safepath-mcp:8000", "localhost:8000", "127.0.0.1:8000"],
    allowed_origins=["http://mcp:8000", "http://safepath-mcp:8000", "http://localhost:8000", "http://127.0.0.1:8000"],
)
```

Without this, cross-container calls get rejected with `421 Misdirected Request` / "Invalid Host header."

## Reliability

`mcp_client.py` fails soft: any connection or protocol error during the SSE call is caught, logged, and swallowed, returning `{}`. `compute_safety_score()` in `main.py` treats a missing component the same way — it re-weights across whatever scores *are* available rather than defaulting the whole route to neutral, and only falls back to a flat 50 if all three sources are missing. A route search never breaks just because the MCP service is temporarily down.

## Known limitations

- **Linear scan performance**: `accident_risk()` and `lighting_density()` scan the full dataset (61,694 accidents / 101,780 lamps) per sampled point. A ~21km route with alternatives measured ~13.7s for the MCP step alone — before OSRM or the LLM summary call are added. Not yet fixed; proposed fix is a spatial index (`scipy.spatial.cKDTree` or a lat/lng grid bucket) built once at startup. Documented in `Docs/SafetyScoreMethodology.md`.
- **Lighting data gaps**: some genuinely safe outer districts (Karow, parts of Grunewald) show 0 lamps within 150m — sparser OpenStreetMap tagging outside central Berlin, not an absence of real lighting.
