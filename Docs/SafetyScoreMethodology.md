# Safety Score Methodology

Background on how SafePath Berlin's route `safetyScore` is calculated. This
covers what data feeds it, how each component is scored, why the current
formulas look the way they do (including two real bugs found and fixed), and
known limitations. For hands-on test cases and live numbers, see
`Docs/RouteScoringTestCases.md` and `Docs/RouteSafetyTestCases.md`.

## Pipeline

1. **OSRM** returns candidate routes between start and destination, using
   either the walking or driving profile per the request's `travelMode`
   (see "Known limitations" below for how each is served).
2. **Backend** (`backend/main.py`) samples each route's polyline every 300m and
   sends all points to the **MCP server** (`backend/mcp/mcp_server.py`) in one
   batch call — `get_routes_safety_context`.
3. MCP looks up real crime, accident, and lighting data for each sample point
   and averages them per route.
4. Backend combines the three averages into one `safetyScore` deterministically
   in Python (`compute_safety_score` in `main.py`) — no LLM involved in the
   numbers themselves.
5. The LLM (LiteLLM, called directly — not routed through Langflow for this
   endpoint) only writes the route `name` and a one-paragraph `summary`,
   grounded in the already-computed scores.

This split matters: the score is deterministic and reproducible (same
input -> same output), and the LLM's job is explanation, not arithmetic.

## The three components

All three are scored 0–100, **higher = safer**, using real Berlin datasets —
never guessed or LLM-estimated.

### Crime Safety (`backend/mcp/crime_lookup.py`)

- **Source**: Berlin police "Fallzahlen & HZ" spreadsheet (2016–2025), matched
  to a point via the official Bezirksregion polygons (`lor_bezirksregionen_2021.geojson`).
- **Metric**: crimes per km² (`fallzahl / region area`), min-max normalized
  across all 143 regions, then inverted (`score = round((1 - pct) * 100)`)
  so fewer crimes per km² = higher score.
- **Why not the official crime rate (HZ = cases per 100k *registered
  residents*)?** That was the original metric, and it was wrong for this use
  case. Areas with almost no official residents but heavy foot traffic
  (Alexanderplatz, government/embassy districts, big parks) get crime
  divided by a tiny population, making the rate look enormous — the
  Regierungsviertel (government quarter) topped the entire city's "danger"
  ranking under this metric, scoring a literal 0/100, purely because almost
  nobody lives there. Switching to crimes-per-km² fixed this: Regierungsviertel
  went from 0 to 80, Tiergarten Süd (mostly parkland) from 39 to 80 — while
  genuine hotspots (Alexanderplatz ~38, Reuterkiez in Neukölln ~0) correctly
  stayed low, since that's real crime density, not a denominator artifact.

### Accident Safety (`backend/mcp/accident_lookup.py`)

- **Source**: Unfallatlas (official German accident data), 2021–2025 combined,
  61,694 Berlin records.
- **Metric**: severity-weighted risk points within 150m of a point
  (severity 1 [fatal] = 3 points, 2 [serious] = 2, 3 [minor] = 1), normalized
  against a ceiling of 150 points, inverted (fewer/less severe nearby
  accidents = higher score).
- This ceiling was checked against real data and holds up: Potsdamer Platz
  (Berlin's worst accident-history location in this dataset, 108 accidents
  within 150m across 5 years) scores 24 — clearly flagged as risky without
  being clipped to a meaningless 0, leaving headroom to still distinguish it
  from an even worse hypothetical spot.

### Lighting Safety (`backend/mcp/lighting_lookup.py`)

- **Source**: OpenStreetMap street lamp nodes (Overpass extract, 101,780
  lamps citywide, June 2026 snapshot).
- **Metric**: lamp density per km² within 150m, min-max normalized against a
  ceiling (`LAMPS_PER_KM2_HIGH`), no inversion (more lamps = higher score).
- **Recalibration story**: the ceiling was originally 600, calibrated from a
  single test point — Potsdamer Platz (~750/km², the single brightest plaza
  in the city). That meant the 0–100 scale ran from "pitch dark" to
  "brightest plaza in Berlin," so almost everywhere else, including normal
  safe streets, read as dim by comparison (a quiet-but-genuinely-safe suburb
  like Müggelheim scored 33; a Grunewald villa street scored 14). Recalibrated
  to 380 — the 90th percentile of a 3,000-point random sample across Berlin,
  filtered to points within 300m of any lamp ("near-road," to exclude lakes
  and forest interior a route would never cross). After the fix: Müggelheim
  86, Regierungsviertel 93, Alexanderplatz 86 — real streets can now reach a
  realistic "well-lit" score instead of only the single brightest known point
  in the city.

## Combining into one score

`compute_safety_score` in `backend/main.py`:

```
safetyScore = (accident*0.35 + crime*0.35 + lighting*0.30) / (sum of weights actually available)
```

- Weights: **accident 35%, crime 35%, lighting 30%**.
- If a component has no data for a route (e.g. a sample point falls outside
  the crime dataset's coverage), it's excluded from both the numerator and
  the weight sum — one missing source doesn't silently drag the score toward
  a default, it just re-weights across what's available. If *all three* are
  missing, the route falls back to a neutral 50.
- `accentColor` / bucket thresholds: **85+ green ("Strong"), 70–84 orange
  ("Balanced"), below 70 red ("Caution")** — same thresholds used both
  backend (`accent_color_for`) and frontend (`getSafetyTone` in
  `frontend/src/data/routeAnalysis.js`).

## Label semantics

The breakdown labels are **"Accident Safety," "Crime Safety," "Lighting
Safety"** — all higher-is-safer, matching `safetyScore` itself. (Earlier
versions used "Accident Risk" / "Crime Level," which read as the opposite
direction — higher number = more danger — while the underlying values were
always safety scores. That mismatch was the actual source of confusion, not
a math error: the weighted average was always correct, e.g.
`0.35×60 + 0.35×37 + 0.30×60 = 51.95 ≈ 52` matched the displayed total
exactly.) The frontend also shows a "Higher score = safer" caption above the
breakdown as a plain-language reminder.

## Known limitations

- **Crime score floor**: Reuterkiez (Neukölln) is the single highest
  crime-density region in the dataset, so it always scores crime = 0 — this
  is the new metric's own ceiling case, not a bug, but worth knowing a route
  through there will always show a 0 there.
- **Lighting data gaps in outer districts**: some genuinely quiet, safe outer
  areas (Karow, parts of Grunewald) show 0 lamps within 150m — this reflects
  sparser OpenStreetMap street-lamp tagging outside central Berlin, not
  necessarily an absence of real lighting. Recalibrating the ceiling can't
  fix a literal zero count; this needs either better source data or a
  fallback strategy (e.g. wider search radius when zero lamps are found).
- **Travel mode**: `/api/routes/safe` now accepts `travelMode: "walking"`
  (default) or `"driving"` (see `RouteRequest` in `main.py`). Walking uses a
  self-hosted OSRM instance with the real foot.lua profile
  (`docker-compose.dev.yml` services `osrm-foot` / `osrm-foot-import` — see
  README "First-time walking-route data build"); driving still uses the
  public OSRM demo server. Note: the public demo server's own `/foot/` path
  does NOT serve real pedestrian data — verified by comparing its `/driving/`
  and `/foot/` responses for identical points, which came back byte-identical
  (same distance/duration) — so walking could not simply reuse that URL.
- **Performance risk on long routes**: `accident_risk()` and
  `lighting_density()` do a linear scan over the full dataset (61,694
  accidents / 101,780 lamps) per sampled point. Measured: a ~21km cross-city
  route (70 samples) takes ~4.6s for the MCP step on a single route, ~13.7s
  once OSRM's alternatives are included — before OSRM's own latency or the
  LLM summary call are added. This can exceed the 10-second response budget
  for long routes. Not yet fixed; the proposed fix is a spatial index
  (`scipy.spatial.cKDTree` or a lat/lng grid bucket) built once at startup so
  radius queries are O(log n) instead of O(n) — see
  `Docs/RouteSafetyTestCases.md` section 4 for the full benchmark.
