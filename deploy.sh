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
cd /app

echo "== git fetch =="
git fetch origin prod
git reset --hard origin/prod
git clean -fd
git log -1 --oneline        # print the commit you're now on

echo "== build =="
docker compose up -d --build
docker compose -f docker-compose-langflow.yml up -d --build