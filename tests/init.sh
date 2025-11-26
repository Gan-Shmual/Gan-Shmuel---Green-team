#!/bin/sh
set -e

BASE="weight-service:5000"

curl --location "http://${BASE}/api/batch-weight" \
--header 'Content-Type: application/json' \
--data '{
  "file": "containers1.csv"
}'

curl --location "http://${BASE}/api/batch-weight" \
--header 'Content-Type: application/json' \
--data '{
  "file": "containers2.csv"
}'


curl --location "http://${BASE}/api/batch-weight" \
--header 'Content-Type: application/json' \
--data '{
  "file": "trucks.json"
}'


curl --location "http://${BASE}/api/weight" \
--header 'Content-Type: application/json' \
--data '{
  "direction": "in",
  "truck": "T-14409",
  "containers": "C-35434,C-73281",
  "weight": 12000,
  "unit": "kg",
  "force": false,
  "produce": "banana"
}
'

curl --location "http://${BASE}/api/weight" \
--header 'Content-Type: application/json' \
--data '{
  "direction": "out",
  "truck": "T-14409",
  "containers": "C-35434,C-73281",
  "weight": 12000,
  "unit": "kg",
  "force": false,
  "produce": "banana"
}
'

pytest /tests/test_service.py -v
