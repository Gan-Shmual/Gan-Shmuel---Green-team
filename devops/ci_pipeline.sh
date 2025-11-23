#!/usr/bin/env bash

set -e

WORKDIR=/workspace
REPO_NAME=Gan-Shmuel---Green-team
REPO_DIR="$WORKDIR/$REPO_NAME"
CI_BRANCH=development
REPO_URL=https://${GITHUB_TOKEN}@github.com/Gan-Shmual/Gan-Shmuel---Green-team.git

log() {
  echo "[CI $(date '+%Y-%m-%d %H:%M:%S')] $1"
}

send_notification() {
  local status=$1
  local message=$2
  python3 /app/send_email.py "CI Pipeline $status" "$message" "$status"
}

log "using workspace : $WORKDIR"
mkdir -p "$WORKDIR"
cd "$WORKDIR"


if [ ! -d "$REPO_DIR/.git" ]; then
    log "Repo not found,cloning..."
    git clone "$REPO_URL" "$REPO_NAME"
else
    log "Repo already exists, skipping clone"
fi

cd "$REPO_DIR"

log "Fetching latest changes from origin..."
git fetch origin

log "Checking out branch: $CI_BRANCH"
git checkout "$CI_BRANCH"

log "Pulling latest changes..."
git pull origin "$CI_BRANCH"

#Test env build and running tests
log "Building test environment"

#to make sure the test env is cleaned up no matter what happens(fail/success)
trap 'log "Cleaning up test environment..."; docker compose -f docker-compose.tests.yml down -v || true' EXIT 
docker compose -f docker-compose.tests.yml up -d --build

log "Test environment built successfully"

sleep 10

log "Running automated tests..."
if docker compose -f docker-compose.tests.yml run --rm test-runner; then
  log "All tests passed!"
else
  log "Tests failed"

  TEST_LOGS=$(docker compose -f docker-compose.tests.yml logs test-runner 2>&1 | tail -100)
  send_notification "failure" "Tests failed in test environment.

Branch: $CI_BRANCH
Time: $(date)
Status: Tests failed

Last 100 lines of logs: 
$TEST_LOGS

Test environment is still running on ports 9001-9002 for debugging."

  exit 1
fi


log "Tests passed! Proceeding to production deployment..."

##building services
log "Creating Pull Request: $CI_BRANCH -> main..."
PR_NUMBER=$(python3 /app/github_api.py create 2>&1 | grep -oP '(?<=Pull Request created: #)\d+' | head -1)

if [ -z "$PR_NUMBER" ]; then
  PR_NUMBER=$(python3 /app/github_api.py create 2>&1 | grep -oP '(?<=Found existing PR: #)\d+' | head -1)
fi

if [ -n "$PR_NUMBER" ]; then
  log "Pull Request #$PR_NUMBER created/found"
  sleep 3

  log "Auto-merging Pull Request #$PR_NUMBER..."
  if python3 /app/github_api.py merge $PR_NUMBER; then
    log "Pull Request merged successfully"
  else
    log "Failed to merge Pull Request"
    send_notification "failure" "Pull Request #$PR_NUMBER could not be merged automatically.
    Please check for merge conflicts at:
    https://github.com/Gan-Shmual/Gan-Shmuel---Green-team/pull/$PR_NUMBER"
    exit 1
  fi
else
  log "Failed to create Pull Request"
  send_notification "failure" "Failed to create Pull Request from $CI_BRANCH to main."
  exit 1
fi

log "Deploying to production..."
docker compose -f docker-compose.prod.yml up -d --build
log "Production deployment finished successfully!"

send_notification "success" "Deployment to production completed successfully.

Branch: $CI_BRANCH
Pull Request: #$PR_NUMBER (merged)
Time: $(date)
Status: All tests passed
Deployment: Production environment updated"

log "CI/CD pipeline completed successfully!"