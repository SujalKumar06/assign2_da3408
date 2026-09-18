#!/usr/bin/env bash

docker build -t spam-classifier:naive -f q1/Dockerfile.naive app/
docker build -t spam-classifier:multi -f q1/Dockerfile.multistage app/
docker images | grep spam-classifier

docker run -d -p 8080:8080 --name spam-naive spam-classifier:naive
sleep 6
curl localhost:8080/healthz; echo
curl -X POST localhost:8080/predict -H "Content-Type: application/json" -d '{"text":"WIN a FREE iPhone now! Click here: bit.ly/xyz123"}'; echo
curl -X POST localhost:8080/predict -H "Content-Type: application/json" -d '{"text":"Hey, are we still meeting for lunch on Friday?"}'; echo
docker stop spam-naive
docker rm spam-naive

docker run -d -p 8080:8080 --name spam-multi spam-classifier:multi
sleep 6
curl localhost:8080/healthz; echo
curl -X POST localhost:8080/predict -H "Content-Type: application/json" -d '{"text":"WIN a FREE iPhone now! Click here: bit.ly/xyz123"}'; echo
curl -X POST localhost:8080/predict -H "Content-Type: application/json" -d '{"text":"Hey, are we still meeting for lunch on Friday?"}'; echo
docker stop spam-multi
docker rm spam-multi
