# SafePath Berlin
🔰 **SafePath Berlin** is an AI-powered safety navigation platform for travelling routes in Berlin. It combines street-lighting data and crime statistics to recommend the safest route between two locations — not just the fastest — and explains that recommendation in simple words with friendly UI.

## ⚙️ Resources
### Openstreetmap 🗺
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

## 👥 Group members
1. Napat Sriwiroj
2. Pantida Luksanajan
3. May Pyae Phyo Thaw
