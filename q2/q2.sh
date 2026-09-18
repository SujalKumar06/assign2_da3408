#!/usr/bin/env bash

docker compose -f q2/docker-compose.yml up -d --build
sleep 10

MSG='{"text":"Congratulations! You have WON a laptop. Claim NOW at tinyurl.com/abc"}'

curl -o /dev/null -w "Initial mssg: %{time_total}s\n" -X POST localhost:8080/predict -H "Content-Type: application/json" -d "$MSG"
curl -o /dev/null -w "Second mssg: %{time_total}s\n" -X POST localhost:8080/predict -H "Content-Type: application/json" -d "$MSG"
