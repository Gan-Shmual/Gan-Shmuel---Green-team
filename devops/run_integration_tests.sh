#!usr/bin/env bash

set -e

REPO_DIR=${1:-/workspace/Gan-Shmuel---Green-team}
COMPOSE_FILE=${2:-docker-compose.tests.yml}

log () {
    echo "[INTEGRATION-TESTS $(date '+%Y-%m-%d %h:%m:%S')] $1"
}

log "Building test environment..."

#to make sure the test env is cleaned up no matter what happens(fail/success)
trap 'log "Cleaning up test environment..."; cd "$REPO_DIR" && docker compose -f "$COMPOSE_FILE" down -v || true' EXIT

cd "$REPO_DIR"

docker compose -f "$COMPOSE_FILE" up -d --build

log "Test environment build successfully"

log "Waiting for services to start..."
sleep 10

#run integarion + e2e tests
if docker compose -f "$COMPOSE_FILE" run --rm test-runner; then
    log "All integration tests passed!"
    exit 0
else
    log "Integarion tests failed"

    TEST_LOGS=$(docker compose -f "$COMPOSE_FILE" logs test-runner 2>&1 | tail -100)

    echo "$TEST_LOGS" > /tmp/integration_test_failure_report.txt

    exit 1
fi