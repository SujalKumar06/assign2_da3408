#!/usr/bin/env bash

minikube delete
minikube start --nodes 2 --cpus 2 --memory 1800 --driver=docker
kubectl get nodes -o wide

docker build -t shard-validator:latest q3/
minikube image load shard-validator:latest

kubectl apply -f q3/indexed-job.yaml

sleep 5
kubectl get pods -o wide

sleep 12
kubectl get pods -o wide

kubectl get job shard-validation-job
kubectl logs -l job-name=shard-validation-job --tail=-1 | grep RESULT_JSON | sort
