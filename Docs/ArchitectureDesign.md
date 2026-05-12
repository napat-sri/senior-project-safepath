# ⚙️ Architecture Design
## Openstreetmap 🗺
This is a container that you can get an image of map from anywhere of the world via a .osm.pbf file. I set up Openstreetmap from [openstreetmap-tile-server](https://github.com/Overv/openstreetmap-tile-server) via Docker container.

<ins>Setting up the server</ins>
1. Create a Docker volume to hold the PostgreSQL database that will contain the OpenStreetMap data:
```
docker volume create berlin-data
```
2. Let the container download a osm.pbf and a .poly file where you are interested from [geofabrik.de](https://download.geofabrik.de/) For example, in this case is Berlin, Germany:
```
docker run \
-e DOWNLOAD_PBF=https://download.geofabrik.de/europe/germany/berlin-latest.osm.pbf \
-e DOWNLOAD_POLY=https://download.geofabrik.de/europe/germany/berlin.poly \
-v berlin-data:/data/database/ \
overv/openstreetmap-tile-server \
import
```

<ins>Running the server</ins>
Run the server:
```
docker run -p 8080:80 -v berlin-data:/data/database/ -d overv/openstreetmap-tile-server run
```
The tiles will avaliable on http://localhost:8080.


# 💬 Langflow
Langflow is a powerful and intuitive platform designed for building, iterating, and deploying AI applications. Leveraging a visual interface, users can effortlessly create flows by dragging and connecting components, making AI app development accessible and efficient.

<ins>Getting Started</ins>
To start using Langflow:
Pull the Docker image corresponding to your desired version.
Use the following command to run Langflow:
```
docker run -it --rm -p 7860:7860 langflowai/langflow:latest
```
Access Langflow at http://localhost:7860 in your web browser.




# 🧩 External APIs
1. `get_crime_data`     – returns Berlin district-level crime density scores (incidents per 1 000 residents) for the area covered by a route.
"BERLIN_CRIME_API_URL","https://www.statistik-berlin-brandenburg.de/opendata"
2. `get_lighting_density` – returns the street-lamp density (lamps per km²) for the area covered by a route, sourced from OpenStreetMap.
"OVERPASS_API_URL", "https://overpass-api.de/api/interpreter"


