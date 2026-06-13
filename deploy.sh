#!/bin/sh
set -e

cd /opt/apps/senior-project-safepath

git fetch origin prod
git reset --hard origin/prod
git clean -fd

docker compose up -d --build

