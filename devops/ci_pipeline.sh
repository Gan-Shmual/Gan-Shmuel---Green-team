#!/usr/bin/env bash

set -e

WORKDIR=/workspace
REPO_NAME=Gan-Shmuel---Green-team
REPO_DIR="$WORKDIR/$REPO_NAME"
CI_BRANCH=dev/testsEnv ##TEMP,i'll change it back to development
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
#Test env build and running tests
echo "[CI]Running test envoirment"
#to make sure the test env is cleaned up no matter what happens(fail/success)
trap 'echo "[CI] Cleaning up test environment..."; docker compose -f docker-compose-tests.yml down -v || true' EXIT 
docker compose -f docker-compose-tests.yml up -d --build
echo "[CI]Test envoirment built successfully"
#testing health for now,we'll add some SQL actions when we get a working version from billing/weight
echo "[CI]Running health checks"


#Need to fix this part,localhosts are not reachable from the docker-compose.test yet
HOST_DOCKER_IP=$(ip route | awk '/default/ {print $3}')
echo "[CI] Host Docker IP: $HOST_DOCKER_IP"
#health check func
check() {
  service=$1
  port=$2

#had to do more attempts to give the service some time to come up(could use a sleep,but since it's EC2 I think a loop is better)
  for i in {1..5}; do
    if curl -fs "http://$HOST_DOCKER_IP:$port/health" >/dev/null; then
      echo "[CI] $service is healthy"
      return 0
    fi
    echo "[CI] $service not ready (try $i/5)"
    sleep 2
  done

  echo "[CI] ERROR: $service failed health check"
  return 1
}




# Run health checks for both services(curl /health for now,we'll add other tests)
check billing 8001
check weight 8002

##################################


echo "[CI]Tests passed!:"
##building services
echo "[CI] Building docker images..."
##this part is where I need to discuss with the team,if we have one SQL container or seperate containers(seperate for now)

# docker build -t billing-service ./billing-service
# docker build -t weight-service ./weight-service


echo "[CI] Docker compose building..."
#docker compose -f docker-compose.yml up -d --build

echo "[CI] Deployment finished successfully"
