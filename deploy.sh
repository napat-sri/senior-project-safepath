#!/bin/sh
cd /app

# 1. Fetch the latest history from the remote repository
git fetch origin

# 2. Force the local prod branch to exactly match the remote prod branch
# This automatically wipes out any accidental local changes on the server!
git reset --hard origin/prod

# 3. Rebuild and restart the Docker containers
docker compose up -d --build