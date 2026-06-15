#!/bin/sh
cd /app

git fetch origin prod
git reset --hard origin/prod
git clean -fd

docker compose up -d --build

docker compose up -f docker-compose-langflow.yml -d --build
