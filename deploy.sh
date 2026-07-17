# #!/bin/sh
# cd /app

# git fetch origin prod
# git reset --hard origin/prod
# git clean -fd

# echo building project stack
# docker compose up -d --build

# echo building langflow stack
# docker compose -f docker-compose-langflow.yml up -d --build

#!/bin/sh
set -eu
git config --global --add safe.directory /app
 
cd /app
 
echo "== git fetch =="
git fetch origin prod
git reset --hard origin/prod
git clean -fd
git log -1 --oneline          # prints the commit now deployed — verify it's the latest
 
echo "== building project stack =="
docker compose up -d --build
 
echo "== building langflow stack =="
docker compose -f docker-compose-langflow.yml up -d --build
 
echo "== deploy complete =="