#!/bin/bash
set -e
# Redirect output to a log file
exec > test_trucks.log 2>&1

echo "-----STARTING TEST-----"
docker compose up --build -d || { echo "compose failed"; exit 1; }

sleep 5

# waiting for mysql
# -s: silent mode, -f: fail if non-2xx
until curl -sf http://localhost:5000/health > /dev/null; do
    echo "Waiting for app to be healthy..."
    sleep 2
done
echo "App is healthy!"
echo "________________________________"

echo "Waiting for sql (max 60s)..."

for (( i=0; i<60; i+=5 )); do
    if curl -s http://localhost:5000/health > /dev/null; then
        echo "Service is up after $i seconds"
        break
    fi
    sleep 5
done

if [ $i -eq 60 ]; then
    echo "Service did not start within 60 seconds. Exiting."
    docker compose down -v
    exit 1
fi

echo "testing updating rates"
curl -v -X POST http://localhost:5000/rates -H "Content-Type: application/json" -d '{"filename": "rates.xlsx"}'
echo ""

echo "testing updating rates"
curl -v -X POST http://localhost:5000/rates/ -F "file=@./sample_rates.xlsx" 
echo ""

docker compose down -v
echo "-----DONE-----"
