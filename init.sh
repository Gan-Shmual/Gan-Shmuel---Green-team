
curl --location 'http://localhost:5000/batch-weight' \
--header 'Content-Type: application/json' \
--data '{
  "file": "containers1.csv"
}'

curl --location 'http://localhost:5000/batch-weight' \
--header 'Content-Type: application/json' \
--data '{
  "file": "containers2.csv"
}'


curl --location 'http://localhost:5000/batch-weight' \
--header 'Content-Type: application/json' \
--data '{
  "file": "trucks.json"
}'

curl --location 'http://localhost:5001/rates' \
--header 'Content-Type: application/json' \
--data '{
    "filename" : "rates.xlsx"
}'

curl --location 'http://localhost:5000/weight' \
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

curl --location 'http://localhost:5000/weight' \
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

curl --location 'http://localhost:5001/provider' \
--header 'Content-Type: application/json' \
--data '{
  "name": "hello"
}'


curl --location 'http://localhost:5001/truck' \
--header 'Content-Type: application/json' \
--data '{
    "provider" : "10001",
    "id" : "T-14409"
}'

