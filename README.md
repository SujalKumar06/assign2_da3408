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

The dataset and model are committed, but regenerate with:

```bash
cd app && python generate_dataset.py && python train.py
```

---

## Q1: Naive vs multi-stage Docker

Comment out the Redis block in `app/main.py` first, or `/predict` returns 500.

```bash
bash q1/q1.sh
```

Builds both images, prints `docker images`, runs each and curls `/healthz` and
`/predict`.

---

## Q2: Docker Compose with a Redis cache

Uncomment the Redis block in `app/main.py` first, or every call is a miss.

```bash
bash q2/q2.sh
```

Brings up `api` + `cache`, sends the same request three times and prints the miss
and hit timings, then tears the stack down.

---

## Q3: Kubernetes Indexed Job

```bash
bash q3/q3.sh
```

Starts a 2-node cluster, loads the image onto both nodes, runs the Job over 8
shards and prints each shard's invalid-row count.

---

## Q4: Deployment, self-healing and rolling updates

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
