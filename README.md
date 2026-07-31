# SafePath Berlin
🔰 **SafePath Berlin** is an AI-powered safety navigation platform for travelling routes in Berlin. It combines street-lighting data and crime statistics to recommend the safest route between two locations — not just the fastest — and explains that recommendation in simple words with friendly UI.

## 🧑‍💻 **Project Vision**
For students, tourists, and commuters in Berlin who want to travel more safely and confidently, SafePath Berlin is an AI-powered safety navigation platform that recommends the safest routes using street-lighting and crime data with simple, friendly explanations, unlike traditional navigation apps that only focus on the fastest route, because our product prioritizes personal safety through intelligent risk analysis and user-centered design.

## 👥 Group members
1. Napat Sriwiroj
2. Pantida Luksanajan
3. May Pyae Phyo Thaw


## Install project dependencies

Install the frontend dependencies from the repository root:

```bash
cd frontend
npm install
```

Install the backend dependencies:

```bash
cd ../backend
pip install -r requirements.txt
```

## Run the project locally

The frontend falls back to localhost defaults in development, so you can start
it without creating an env file. If you want to override any values, copy
`frontend/.env.development.example` to `frontend/.env.development`.

Start the backend API on port 9000:

```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 9000 --reload
```

In a second terminal, start the frontend on port 8080:

```bash
cd frontend
npm run dev
```

For a production-style frontend build, copy
`frontend/.env.production.example` to `frontend/.env.production` before
running `npm run build`.

## Run with Docker

For local development with Docker, use the separate dev compose file:

```bash
docker compose -f docker-compose.dev.yml up --build
```

That stack publishes the frontend on 8080, the backend on 9000, and Langflow on 7860, without the Caddy/VPN/tile-server wiring from the production compose files.

### First-time map import (tile server)

The OpenStreetMap tile server uses a pre-populated `berlin-data` volume. On a fresh machine you MUST run the one-time import before starting the services. The import downloads and imports a large Berlin extract and can take 20–60 minutes and tens of GB of disk.

Run this once only on first setup:

```bash
# Run the OSM import (one-shot) — only on first run
docker compose --profile setup run --rm osm-import
```

After the import completes, start the services as normal:

```bash
docker compose up --build
```

If you do not need the tile server locally, skip the import step — the rest of the stack will run without it.

The frontend runs on port 8080, the backend on port 9000, Langflow on port 7860, and the tile server on port 8081.

### First-time walking-route data build (osrm-foot)

Walking directions (`travelMode: "walking"`) are served by a self-hosted OSRM
instance, not the public demo server — the public server only has a driving
dataset (its `/foot/` path silently returns driving-speed results instead of
erroring). This also needs a one-time data build on a fresh machine, using
`docker-compose.dev.yml`:

```bash
# Run once only on first setup, IN ORDER — downloads Berlin's .osm.pbf, then
# builds the OSRM foot-profile dataset from it. Takes a few minutes total.
docker compose -f docker-compose.dev.yml --profile setup run --rm osrm-foot-download
docker compose -f docker-compose.dev.yml --profile setup run --rm osrm-foot-import
```

(Two separate steps because the `osrm/osrm-backend` image itself is built on
an EOL Debian release with dead apt mirrors, so it can't reliably install a
downloader — the small Alpine-based `osrm-foot-download` step fetches the
file into the shared volume instead.)

After it completes, start the stack as normal and `travelMode: "walking"`
requests to `/api/routes/safe` will route through `osrm-foot`. If you skip
this step, walking requests will fail to reach OSRM until it's run — driving
requests are unaffected either way.
