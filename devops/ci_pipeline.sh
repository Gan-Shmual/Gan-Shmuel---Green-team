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

log "Running unit tests"

if /app/run_unit_tests.sh "$REPO_DIR"; then
  log "Unit tests passed"
else
  log "Unit tests failed"

  FAILURE_REPORT=$(cat /tmp/unit_test_failure_report.txt 2>/dev/null || echo "Check logs for details")
  
    send_notification "failure" "Unit tests failed.

Branch: $CI_BRANCH
Time: $(date)

$FAILURE_REPORT"

    exit 1
fi

#set up test environment
log "Running integartion tests..."
if /app/run_integration_tests.sh "$REPO_DIR" "docker-compose.tests.yml"; then
  log "Integration tests passed"
else
  log "integration tests failed"

  TEST_LOGS=$(cat /tmp/integration_test_failure_report.txt 2>/dev/null || echo "Check logs for details")

  send_notification "failure" "Integration tests failed in test environment.

Branch: $CI_BRANCH
Time: $(date)
Status: Tests failed
 
$TEST_LOGS"

  exit 1
fi

log "All tests passed! Proceeding to production deployment..."

#create and merge pull request
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

COMMIT_SHA=$(git -C "$REPO_DIR" rev-parse HEAD)

#deploy to production
log "Deploying to production..."
if /app/deploy.sh "$REPO_DIR" "docker-compose.prod.yml"; then
  log "Deployment successful"

  send_notification "success" "Deployment to production completed successfully.

Branch: $CI_BRANCH
Pull Request: #$PR_NUMBER (merged)
Commit: $COMMIT_SHA
Time: $(date)
Status: All tests passed
Deployment: Production environment updated"

  log "CI/CD pipeline completed successfully!"
  exit 0
else
  log "Deployment failed"
  send_notification "failure" "Deployment to production failed

Branch: $CI_BRANCH
Pull request: #$PR_NUMBER (merged)
Time: $(date)
Status: Deployment step failed"
  exit 1
fi