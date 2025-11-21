#!/usr/bin/env bash

set -e

WORKDIR=/workspace
REPO_NAME=Gan-Shmuel---Green-team
REPO_DIR="$WORKDIR/$REPO_NAME"
CI_BRANCH=development
REPO_URL=https://${GITHUB_TOKEN}@github.com/Gan-Shmual/Gan-Shmuel---Green-team.git

echo "[CI] using workspace : $WORKDIR"
mkdir -p "$WORKDIR"
cd "$WORKDIR"


if [ ! -d "$REPO_DIR/.git" ]; then
    echo "[CI] Repo not found,cloning..."
    git clone "$REPO_URL" "$REPO_NAME"
else
    echo "[CI] Repo already exists, skipping clone"
fi

cd "$REPO_DIR"

echo "[CI] Fetching latest changes from origin..."
git fetch origin

echo "[CI] Checking out branch: $CI_BRANCH"
git checkout "$CI_BRANCH"

echo "[CI] Pulling latest changes..."
git pull origin "$CI_BRANCH"

##building services
echo "[CI] Building docker images..."
##this part is where I need to discuss with the team,if we have one SQL container or seperate containers(seperate for now)

# docker build -t billing-service ./billing-service
# docker build -t weight-service ./weight-service


echo "[CI] Docker compose building..."
docker-compose -f docker-compose.yml up -d --build

echo "[CI] Deployment finished successfully"
