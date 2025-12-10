#!/bin/bash

BASE_URL="http://127.0.0.1:5000/api"

echo "1. Testing CREATE Protocol"
curl -X POST $BASE_URL/protocols \
  -H "Content-Type: application/json" \
  -d '{"protocol_name": "Test Protocol", "protocol_symbol": "TEST", "type": "DEX", "description": "Test description"}'

echo "\n\n2. Testing GET All Protocols"
curl -X GET $BASE_URL/protocols

echo "\n\n3. Testing GET Single Protocol"
curl -X GET $BASE_URL/protocols/1

echo "\n\n4. Testing UPDATE Protocol"
curl -X PUT $BASE_URL/protocols/1 \
  -H "Content-Type: application/json" \
  -d '{"description": "Updated description"}'

echo "\n\n5. Testing Protocol Stats"
curl -X GET $BASE_URL/protocols/stats

echo "\n\n6. Testing Transaction Volume Over Time"
curl -X GET "$BASE_URL/transactions/volume-over-time?days=30"

echo "\n\n7. Testing Market Trends"
curl -X GET "$BASE_URL/market/trends?days=7"

echo "\n\n8. Testing DELETE Protocol"
curl -X DELETE $BASE_URL/protocols/1
