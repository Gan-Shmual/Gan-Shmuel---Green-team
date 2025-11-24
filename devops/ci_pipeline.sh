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

log "Running unit tests in parallel..."

#run billing unit tests in background
if [ -d "$REPO_DIR/billing-service/tests" ]; then
    log "Starting billing unit tests..."
    (
      cd "$REPO_DIR/billing-service"
      if pytest tests/ -v; then
          echo "BILLING_PASS" > /tmp/billing_test_result
      else
          echo "BILLING_FAIL" > /tmp/billing_test_result
      fi
    ) &
    BILLING_PID=$!
  else
    log "No unit tests found for billing-service, skipping..."
    echo "BILLING_SKIP" > /tmp/billing_test_result
fi

#run weight unit tests in background
if [ -d "$REPO_DIR/weight-service/tests" ]; then
    log "Starting weight unit tests..."
    (
      cd "$REPO_DIR/weight-service"
      if pytest tests/ -v; then
          echo "WEIGHT_PASS" > /tmp/weight_test_result
      else
          echo "WEIGHT_FAIL" > /tmp/weight_test_result
      fi
    ) &
    WEIGHT_PID=$!
  else
    log "No unit tests found for weight-service, skipping..."
    echo "WEIGHT_SKIP" > /tmp/weight_test_result
fi

#wait for both to complete
if [ -n "$BILLING_PID" ]; then
    wait $BILLING_PID
fi
if [ -n "$WEIGHT_PID" ]; then
    wait $WEIGHT_PID
fi

#check results
BILLING_RESULT=$(cat /tmp/billing_test_result 2>/dev/null || echo "BILLING_SKIP")
WEIGHT_RESULT=$(cat /tmp/weight_test_result 2>/dev/null || echo "WEIGHT_SKIP")

log "Billing tests: $BILLING_RESULT"
log "Weight tests: $WEIGHT_RESULT"

#clean up tmp files
rm -f /tmp/billing_test_result /tmp/weight_test_result

#check if any failed
if [ "$BILLING_RESULT" = "BILLING_FAIL" ] || [ "$WEIGHT_RESULT" = "WEIGHT_FAIL" ]; then
    log "Unit tests failed"

    FAILED_SERVICES=""
    [ "$BILLING_RESULT" = "BILLING_FAIL" ] && FAILED_SERVICES="billing-service"
    [ "$WEIGHT_RESULT" = "WEIGHT_FAIL" ] && FAILED_SERVICES="weight-service"

    send_notification "failure" "Unit tests failed.

Branch: $CI_BRANCH
Time: $(date)
Failed services: $FAILED_SERVICES

check the logs for details."
    exit 1
fi

log "All unit tests passed!"

cd "$REPO_DIR"

#Test env build and running tests
log "Building test environment"

#to make sure the test env is cleaned up no matter what happens(fail/success)
trap 'log "Cleaning up test environment..."; docker-compose -f docker-compose.tests.yml down -v || true' EXIT

docker-compose -f docker-compose.tests.yml up -d --build
log "Test environment built successfully"

log "Waiting for services to start..."
sleep 10

log "Running integration tests..."
if docker-compose -f docker-compose.tests.yml run --rm test-runner; then
  log "All integration tests passed!"
else
  log "Integration tests failed"

  TEST_LOGS=$(docker-compose -f docker-compose.tests.yml logs test-runner 2>&1 | tail -100)
  send_notification "failure" "Integration tests failed in test environment.

Branch: $CI_BRANCH
Time: $(date)
Status: Tests failed

Last 100 lines of logs: 
$TEST_LOGS"

  exit 1
fi


log "All tests passed! Proceeding to production deployment..."

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
docker-compose -f docker-compose.prod.yml up -d --build
log "Production deployment finished successfully!"

log "Tracking deployment"
COMMIT_SHA=$(git rev-parse HEAD)

if [ -f "$WORKDIR/current_deployment.txt" ]; then
    mv "$WORKDIR/current_deployment.txt" "$WORKDIR/previous_deployment.txt"
fi
echo "$COMMIT_SHA" > "$WORKDIR/current_deployment.txt"

log "Deployment tracked: $COMMIT_SHA"

send_notification "success" "Deployment to production completed successfully.

Branch: $CI_BRANCH
Pull Request: #$PR_NUMBER (merged)
Commit: $COMMIT_SHA
Time: $(date)
Status: All tests passed
Deployment: Production environment updated"

log "CI/CD pipeline completed successfully!"