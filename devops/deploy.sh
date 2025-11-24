#!/usr/bin/env bash

set -e

REPO_DIR=${1:-/workspace/Gan-Shmuel---Green-team}
COMPOSE_FILE=${2:-docker-compose.prod.yml}

log () {
    echo "[DEPLOY $(date '+%Y-%m-%d %H:%M:%S')] $1"
}

cd "$REPO_DIR"

docker compose -f "$COMPOSE_FILE" up -d --build

#track deployment for rollback
log "Tracking deployment..."
COMMIT_SHA=$(git rev-parse HEAD)

WORKSPACE_DIR=$(dirname "$REPO_DIR")
if [ -f "$WORKSPACE_DIR/current_deployment.txt" ]; then
    mv "$WORKSPACE_DIR/current_deployment.txt" "$WORKSPACE_DIR/previous_deployment.txt"
fi
echo "$COMMIT_SHA" > "$WORKSPACE_DIR/current_deployment.txt"

log "Deployment tracked: $COMMIT_SHA"

exit 0