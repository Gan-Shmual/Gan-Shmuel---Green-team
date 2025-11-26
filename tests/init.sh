#!/bin/sh
set -e

BASE="weight-service:5000"

curl --location "http://${BASE}/batch-weight" \
--header 'Content-Type: application/json' \
--data '{
  "file": "containers1.csv"
}'
echo ""

curl --location "http://${BASE}/batch-weight" \
--header 'Content-Type: application/json' \
--data '{
  "file": "containers2.csv"
}'
echo ""


curl --location "http://${BASE}/batch-weight" \
--header 'Content-Type: application/json' \
--data '{
  "file": "trucks.json"
}'
echo ""


curl --location "http://${BASE}/weight" \
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

curl --location "http://${BASE}/weight" \
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

pytest /tests/test_service.py -v
