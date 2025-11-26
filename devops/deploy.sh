#!/usr/bin/env bash

set -e

REPO_DIR=${1:-/workspace/Gan-Shmuel---Green-team}
COMPOSE_FILE=${2:-docker-compose.prod.yml}

log () {
    echo "[DEPLOY $(date '+%Y-%m-%d %H:%M:%S')] $1"
}

cd "$REPO_DIR"

# Create .env file in the workspace with environment variables passed from CI container
log "Creating .env file with environment variables..."
cat > .env <<EOF
# Database configuration for weight-service
DB_HOST=${DB_HOST:-weight-db}
DB_USER=${DB_USER:-root}
DB_PASSWORD=${DB_PASSWORD:-root}
DB_NAME=${DB_NAME:-weight}
DB_PORT=${DB_PORT:-3306}
MYSQL_HOST=${MYSQL_HOST:-weight-db}
MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD:-root}
MYSQL_DATABASE=weight
MYSQL_PASSWORD=${MYSQL_PASSWORD:-root}
MYSQL_PORT=${MYSQL_PORT:-3306}

# Database configuration for billing-service
BILLING_DB_HOST=${BILLING_DB_HOST:-db}
BILLING_DB_USER=${BILLING_DB_USER:-root}
BILLING_DB_NAME=${BILLING_DB_NAME:-billdb}
BILLING_DB_PASSWORD=${BILLING_DB_PASSWORD:-pss11}
BILLING_DB_PORT=${BILLING_DB_PORT:-3307}

# Application ports
APP_PORT=${APP_PORT:-5001}
WEIGHTS_PORT=${WEIGHTS_PORT:-5000}
WEIGHTS_HOST=${WEIGHTS_HOST:-weight-service}
EOF

# Fix: When running docker via mounted socket from inside a container,
# docker needs to access paths on the HOST filesystem.
log "Setting up Docker Compose with correct project directory..."

# Calculate the host path for the current repo directory
HOST_REPO_PATH="${HOST_PROJECT_ROOT}/ci-workspace/Gan-Shmuel---Green-team"

log "Container path: $REPO_DIR"
log "Host path: $HOST_REPO_PATH"

docker compose --project-directory "$HOST_REPO_PATH" -f "$COMPOSE_FILE" up -d --build

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