#!/usr/bin/env bash

set -e 

echo "[ROLLBACK] Starting rollback..."

REPO_DIR="/workspace/Gan-Shmuel---Green-team"
PREV_FILE="/workspace/previous_deployment.txt"

cd "$REPO_DIR"

if [ ! -f "$PREV_FILE" ]; then
    echo "ERROR: Previous deployment file not found: $PREV_FILE"
    exit 1
fi

PREVIOUS_COMMIT=$(cat "$PREV_FILE")

if [ -z "$PREVIOUS_COMMIT" ]; then
    echo "ERROR: Previous deployment hash is empty"
    exit 1
fi

echo "[ROLLBACK] Rolling back to: $PREVIOUS_COMMIT"

git fetch origin 
git checkout "$PREVIOUS_COMMIT"

echo "[ROLLBACK] Rebuilding production..."
docker-compose -f docker-compose.prod.yml up -d --build

echo "[ROLLBACK] complete!"