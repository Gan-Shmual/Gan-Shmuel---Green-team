#!/bin/bash
set -e
# Redirect output to a log file
exec > test_trucks.log 2>&1

echo "-----STARTING TEST-----"
docker compose up --build -d || { echo "compose failed"; exit 1; }
sleep 5

# waiting for mysql
echo "Waiting for sql (max 60s)..."

for (( i=0; i<12; i+=5 )); do
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
echo "App is healthy!"
echo "________________________________"

echo "Adding a provider:" 
curl -X POST http://localhost:5000/provider -H "Content-Type: application/json" -d '{"name": "Provider1"}' 
echo "" 

echo "Adding a provider:" 
curl -X POST http://localhost:5000/provider -H "Content-Type: application/json" -d '{"name": "Provider2"}' 
echo ""

echo "Adding a truck:" 
curl -X POST http://localhost:5000/truck -H "Content-Type: application/json" -d '{"id": "1234", "provider": 1}' 
echo ""
echo "Updating the truck info:" 
curl -X PUT http://localhost:5000/truck/1234 -H "Content-Type: application/json" -d '{"provider": 2}'
echo ""

docker compose down -v
echo "-----DONE-----"
