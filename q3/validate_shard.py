"""
validate_shard.py — AIOps Module 3 Assignment, Q3
Entry point for each pod of the Kubernetes Indexed Job. Validates one shard.
"""
import csv
import json
import os
import re
import socket
import time

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
REQUIRED = ["user_id", "email", "signup_date", "country"]


def is_invalid(row):
    if any(not row.get(field, "").strip() for field in REQUIRED):
        return True
    return not EMAIL_RE.match(row["email"].strip())


def main():
    completion_index = int(os.environ.get("JOB_COMPLETION_INDEX", "0"))
    data_dir = os.environ.get("DATA_DIR", "/app/data")
    pod_name = os.environ.get("POD_NAME", socket.gethostname())
    node_name = os.environ.get("NODE_NAME", "unknown")

    shard_path = os.path.join(data_dir, f"shard_{completion_index}.csv")
    print(f"[worker {completion_index}] pod={pod_name} node={node_name} shard={shard_path}", flush=True)

    t0 = time.time()
    total_rows = 0
    invalid_rows = 0
    with open(shard_path, newline="") as f:
        for row in csv.DictReader(f):
            total_rows += 1
            if is_invalid(row):
                invalid_rows += 1
    elapsed = time.time() - t0

    result = {
        "completion_index": completion_index,
        "shard": f"shard_{completion_index}.csv",
        "total_rows": total_rows,
        "invalid_rows": invalid_rows,
        "elapsed_seconds": round(elapsed, 3),
        "pod_name": pod_name,
        "node_name": node_name,
    }
    print("RESULT_JSON:" + json.dumps(result), flush=True)
    time.sleep(int(os.environ.get("HOLD_SECONDS", "0")))


if __name__ == "__main__":
    main()
