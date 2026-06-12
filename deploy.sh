#!/bin/sh
cd /app
# git pull origin prod
# 1. Fetch the latest updates from the remote repository
git fetch origin prod

# 2. Force-reset the local branch to match remote exactly (wipes out permission locks)
git reset --hard origin/prod

# 3. Clean up any untracked leftover files or build debris
git clean -df
docker compose up -d --build
chmod +x deploy.sh
