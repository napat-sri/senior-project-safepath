"""SafePath API.

Endpoints:
  GET  /             - banner
  GET  /api/health   - liveness check
  POST /api/routes   - candidate routes between two points (via OSRM)
"""

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="SafePath API")

# Allow the Vue dev server to call this API from the browser.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://127.0.0.1:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Point(BaseModel):
    lat: float
    lng: float


class RouteRequest(BaseModel):
    start: Point
    destination: Point


@app.get("/")
def root():
    return {"message": "Welcome to SafePath API"}


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/test")
def test():
    return {"data": [{"id": 1,"name": "Route 1"}, {"id": 2,"name": "Route 2"}, {"id": 3,"name": "Route 3"   }]}

@app.post("/api/routes")
def get_routes(req: RouteRequest):
    """Return candidate routes between start and destination.
    """      
    routes = []
    routes.append({
        "distance": 1000,
        "duration": 600,
        "geometry": {
            "type": "LineString",
            "coordinates": [
                [req.start.lng, req.start.lat],
                [req.destination.lng, req.destination.lat]
            ]
        }
    })
    routes.append({
        "distance": 1200,
        "duration": 720,
        "geometry": {
            "type": "LineString",
            "coordinates": [
                [req.start.lng, req.start.lat],
                [req.destination.lng, req.destination.lat]
            ]
        }
    })      

    return {"routes": routes}
