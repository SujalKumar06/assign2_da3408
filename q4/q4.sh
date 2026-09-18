#!/usr/bin/env bash

docker build -t spam-api:v1 -f q1/Dockerfile.multistage app/
minikube image load spam-api:v1

kubectl apply -f q4/deployment.yaml -f q4/service.yaml
kubectl rollout status deployment/spam-api
kubectl get pods -o wide
curl $(minikube service spam-api-svc --url)/healthz; echo

kubectl delete pod $(kubectl get pods -l app=spam-api -o jsonpath='{.items[0].metadata.name}')
sleep 8
kubectl get pods -o wide
kubectl get events --sort-by=.lastTimestamp | tail -12

# bump the /healthz version string in app/main.py before this point
docker build -t spam-api:v2 -f q1/Dockerfile.multistage app/
minikube image load spam-api:v2

kubectl annotate deployment/spam-api kubernetes.io/change-cause="v2: add version field to /healthz" --overwrite
kubectl set image deployment/spam-api predictor=spam-api:v2
kubectl rollout status deployment/spam-api
kubectl rollout history deployment/spam-api
kubectl get rs
kubectl get pods -o wide
curl $(minikube service spam-api-svc --url)/healthz; echo
