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

## Run with Docker

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

test hook
