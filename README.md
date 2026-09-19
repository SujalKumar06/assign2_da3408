# AI Operations (AIOps): Assignment 2

Structure of the repository:

```
report.pdf   written answers for Q1-Q4
app/         the spam-detection API
q1/          naive vs multi-stage Docker
q2/          Docker Compose with a Redis cache
q3/          Kubernetes Indexed Job
q4/          Deployment, self-healing and rolling update
```

The answers for all four questions are in `report.pdf`. Terminal output and
screenshots are in `qN/evidence/`.

## Environment

```bash
conda activate aiops
pip install -r app/requirements.txt
```

Docker, `minikube` and `kubectl` must be installed. Run every script from the
repository root, not from inside `qN/`.

```
main.py                the FastAPI service (POST /predict, GET /healthz)
train.py               trains the TF-IDF + MultinomialNB pipeline
generate_dataset.py    generates spam_dataset.csv
spam_dataset.csv       1000 labelled messages
model.joblib           the trained model loaded at startup
requirements.txt       full dependencies, used by the naive image
requirements-multi.txt runtime-only dependencies, used by the multi-stage image
```

The dataset and model are committed, but regenerate with:

```bash
cd app && python generate_dataset.py && python train.py
```

---

## Q1: Naive vs multi-stage Docker

```
Dockerfile.naive        single-stage build, installs requirements.txt
Dockerfile.multistage   builder venv + slim runtime, installs requirements-multi.txt
q1.sh                   builds both, prints sizes, runs and curls each
```

Comment out the Redis block in `app/main.py` first, or `/predict` returns 500.

```bash
bash q1/q1.sh
```

Builds both images, prints `docker images`, runs each and curls `/healthz` and
`/predict`.

---

## Q2: Docker Compose with a Redis cache

```
docker-compose.yml   api service + redis:7-alpine cache service
q2.sh                brings the stack up, times a miss and two hits, tears it down
```

Uncomment the Redis block in `app/main.py` first, or every call is a miss.

```bash
bash q2/q2.sh
```

Brings up `api` + `cache`, sends the same request three times and prints the miss
and hit timings, then tears the stack down.

---

## Q3: Kubernetes Indexed Job

```
data/                 8 CSV shards of signup records
generate_shards.py    regenerates the shards with a seeded invalid-row count
validate_shard.py     worker: validates one shard, prints its result as JSON
Dockerfile            packages the worker and all 8 shards
indexed-job.yaml      the Indexed Job (completions 8, parallelism 4)
q3.sh                 starts the cluster, runs the Job, collects the results
```

```bash
bash q3/q3.sh
```

Starts a 2-node cluster, loads the image onto both nodes, runs the Job over 8
shards and prints each shard's invalid-row count.

---

## Q4: Deployment, self-healing and rolling updates

```
deployment.yaml   2 replicas, CPU requests/limits, readinessProbe on /healthz
service.yaml      NodePort Service fronting the pods
q4.sh             deploys, deletes a pod, then rolls v1 to v2
```

Run Q3 before Q4; `q3.sh` starts with `minikube delete`.

`v1` and `v2` differ only by the `version` string in `/healthz`, so the script
needs a pause partway through:

1. set it to `"v1"` in `app/main.py`
2. run `bash q4/q4.sh` down to the self-healing section
3. change it to `"v2"`
4. continue from the `spam-api:v2` build

For the zero-downtime evidence, run this in a second terminal before
`kubectl set image`:

```bash
URL=$(minikube service spam-api-svc --url)
while true; do curl -s -o /dev/null -w "%{http_code} " $URL/healthz; sleep 0.3; done
```
