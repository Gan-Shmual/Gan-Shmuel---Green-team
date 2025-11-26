#!/usr/bin/env bash

set -e

REPO_DIR=${1:-/workspace/Gan-Shmuel---Green-team}
COMPOSE_FILE=${2:-docker-compose.tests.yml}

log () {
    echo "[INTEGRATION-TESTS $(date '+%Y-%m-%d %H:%M:%S')] $1"
}

log "Building test environment..."

#to make sure the test env is cleaned up no matter what happens(fail/success)
trap 'log "Cleaning up test environment..."; cd "$REPO_DIR" && docker compose --project-directory "${HOST_PROJECT_ROOT}/ci-workspace/Gan-Shmuel---Green-team" -f "$COMPOSE_FILE" down -v || true' EXIT

cd "$REPO_DIR"

# Create .env file in the workspace with environment variables passed from CI container
log "Creating .env file with environment variables..."
cat > .env <<EOF
# Database configuration for weight-service (DB_* variables)
DB_HOST=${DB_HOST:-weight-db}
DB_USER=${DB_USER:-root}
DB_PASSWORD=${DB_PASSWORD:-root}
DB_NAME=${DB_NAME:-weight}
DB_PORT=${DB_PORT:-3306}

# Database configuration for weight-service (MYSQL_* variables - for older compose files)
MYSQL_HOST=${MYSQL_HOST:-weight-db}
MYSQL_USER=${DB_USER:-root}
MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD:-root}
MYSQL_PASSWORD=${MYSQL_PASSWORD:-root}
MYSQL_DATABASE=${DB_NAME:-weight}
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
# Container path: /workspace/Gan-Shmuel---Green-team
# Host path: $HOST_PROJECT_ROOT/ci-workspace/Gan-Shmuel---Green-team
log "Setting up Docker Compose with correct project directory..."

# Calculate the host path for the current repo directory
HOST_REPO_PATH="${HOST_PROJECT_ROOT}/ci-workspace/Gan-Shmuel---Green-team"

log "Container path: $REPO_DIR"
log "Host path: $HOST_REPO_PATH"

# Fix the weight-service environment variables if the compose file uses MYSQL_* instead of DB_*
# The weight-service code expects DB_* variables, but some compose files use MYSQL_* variables
if grep -q "MYSQL_HOST.*weight-db" "$COMPOSE_FILE"; then
    log "Fixing weight-service environment variables in compose file..."
    # Add DB_* variables to weight-service environment section
    sed -i '/weight-service:/,/^  [a-z]/ {
        /MYSQL_HOST=weight-db/a\      - DB_HOST=weight-db\n      - DB_USER=root\n      - DB_PASSWORD=${MYSQL_ROOT_PASSWORD}\n      - DB_NAME=${DB_NAME}
    }' "$COMPOSE_FILE"
fi

# Use --project-directory to tell docker where to resolve relative paths from (on the host)
docker compose --project-directory "$HOST_REPO_PATH" -f "$COMPOSE_FILE" up -d --build 2>&1 | tee /tmp/docker_compose_output.log

log "Test environment built successfully"

log "Waiting for services to start..."
sleep 10

# Check if weight-db container is running, if not capture logs
if ! docker compose --project-directory "$HOST_REPO_PATH" -f "$COMPOSE_FILE" ps weight-db | grep -q "Up\|running"; then
    log "ERROR: weight-db container failed to start properly"
    docker compose --project-directory "$HOST_REPO_PATH" -f "$COMPOSE_FILE" logs weight-db > /tmp/weight_db_failure_logs.txt 2>&1
    cat /tmp/weight_db_failure_logs.txt
    log "Weight-db logs saved to /tmp/weight_db_failure_logs.txt"
    exit 1
fi

#run integarion + e2e tests
if docker compose --project-directory "$HOST_REPO_PATH" -f "$COMPOSE_FILE" run --rm test-runner; then
    log "All integration tests passed!"
    exit 0
else
    log "Integraion tests failed"

    TEST_LOGS=$(docker compose --project-directory "$HOST_REPO_PATH" -f "$COMPOSE_FILE" logs test-runner 2>&1 | tail -100)

    echo "$TEST_LOGS" > /tmp/integration_test_failure_report.txt

    exit 1
fi