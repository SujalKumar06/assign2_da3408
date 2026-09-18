#!/usr/bin/env bash

minikube delete
minikube start --cpus 4 --memory 2500 --driver=docker
kubectl get nodes -o wide

docker build -t spam-api:v1 -f q1/Dockerfile.multistage app/
minikube image load spam-api:v1

kubectl apply -f q4/deployment.yaml -f q4/service.yaml
kubectl rollout status deployment/spam-api
kubectl get pods -o wide

curl $(minikube service spam-api-svc --url)/healthz; echo

kubectl get pods -o wide
kubectl delete pod $(kubectl get pods -l app=spam-api -o jsonpath='{.items[0].metadata.name}')
sleep 8
kubectl get pods -o wide
kubectl get events --sort-by=.lastTimestamp | tail -12

# change the healthz/ code here
docker build -t spam-api:v2 -f q1/Dockerfile.multistage app/
minikube image load spam-api:v2

# zero-downtime check - run in another terminal first:
# URL=$(minikube service spam-api-svc --url)
# while true; do curl -s -o /dev/null -w "%{http_code} " $URL/healthz; sleep 0.3; done

kubectl set image deployment/spam-api predictor=spam-api:v2
kubectl rollout status deployment/spam-api
kubectl rollout history deployment/spam-api
kubectl get rs
kubectl get pods -o wide

curl $(minikube service spam-api-svc --url)/healthz; echo
