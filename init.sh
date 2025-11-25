#!/bin/bash

# Initialize Gan Shmuel services with test data
# Usage: ./init.sh [WEIGHT_HOST:WEIGHT_PORT] [BILLING_HOST:BILLING_PORT]
# Example: ./init.sh localhost:5000 localhost:5001

# Default values
WEIGHT_SERVICE="${1:-localhost:5000}"
BILLING_SERVICE="${2:-localhost:5001}"

echo "Initializing services..."
echo "Weight Service: http://$WEIGHT_SERVICE"
echo "Billing Service: http://$BILLING_SERVICE"
echo ""

# Load container weights (batch 1)
echo "Loading container batch 1..."
curl --location "http://$WEIGHT_SERVICE/batch-weight" \
--header 'Content-Type: application/json' \
--data '{
  "file": "containers1.csv"
}'
echo ""

# Load container weights (batch 2)
echo "Loading container batch 2..."
curl --location "http://$WEIGHT_SERVICE/batch-weight" \
--header 'Content-Type: application/json' \
--data '{
  "file": "containers2.csv"
}'
echo ""

# Load truck weights
echo "Loading truck weights..."
curl --location "http://$WEIGHT_SERVICE/batch-weight" \
--header 'Content-Type: application/json' \
--data '{
  "file": "trucks.json"
}'
echo ""

# Load billing rates
echo "Loading billing rates..."
curl --location "http://$BILLING_SERVICE/rates" \
--header 'Content-Type: application/json' \
--data '{
    "filename" : "rates.xlsx"
}'
echo ""

# Create test weight entry (in)
echo "Creating test weight entry (in)..."
curl --location "http://$WEIGHT_SERVICE/weight" \
--header 'Content-Type: application/json' \
--data '{
  "direction": "in",
  "truck": "T-14409",
  "containers": "C-35434,C-73281",
  "weight": 12000,
  "unit": "kg",
  "force": false,
  "produce": "banana"
}'
echo ""

# Create test weight entry (out)
echo "Creating test weight entry (out)..."
curl --location "http://$WEIGHT_SERVICE/weight" \
--header 'Content-Type: application/json' \
--data '{
  "direction": "out",
  "truck": "T-14409",
  "containers": "C-35434,C-73281",
  "weight": 12000,
  "unit": "kg",
  "force": false,
  "produce": "banana"
}'
echo ""

# Create test provider
echo "Creating test provider..."
curl --location "http://$BILLING_SERVICE/provider" \
--header 'Content-Type: application/json' \
--data '{
  "name": "hello"
}'
echo ""

# Register truck with provider
echo "Registering truck with provider..."
curl --location "http://$BILLING_SERVICE/truck" \
--header 'Content-Type: application/json' \
--data '{
    "provider" : "10001",
    "id" : "T-14409"
}'
echo ""

echo "Initialization complete!"