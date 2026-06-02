#!/bin/bash
cd /opt/apps/senior-project-safepath
git pull origin prod
docker compose up -d --build
chmod +x deploy.sh
