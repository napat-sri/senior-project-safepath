#!/bin/sh
cd /app

git fetch origin prod
git reset --hard origin/prod
git clean -fd

docker compose up -d --build

