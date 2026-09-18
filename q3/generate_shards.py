"""
generate_shards.py — AIOps Module 3 Assignment, Q3
Generates 8 deterministic shards of user signup records, each with a known
number of deliberately invalid rows.
"""
import argparse
import csv
import os
import random

FIELDS = ["user_id", "email", "signup_date", "country"]
FIRST_NAMES = ["alice", "bob", "carol", "dave", "erin", "frank", "grace", "heidi"]
DOMAINS = ["example.com", "mail.org", "corp.net", "webmail.in"]
COUNTRIES = ["IN", "US", "DE", "JP", "BR"]


def corrupt(row, rng):
    kind = rng.choice(["no_at", "no_domain", "empty_email", "no_date", "no_country"])
    if kind == "no_at":
        row["email"] = row["email"].replace("@", ".")
    elif kind == "no_domain":
        row["email"] = row["email"].split("@")[0] + "@"
    elif kind == "empty_email":
        row["email"] = ""
    elif kind == "no_date":
        row["signup_date"] = ""
    else:
        row["country"] = ""
    return row


def generate(shard_index, n_rows=100, seed=42):
    rng = random.Random(seed + shard_index)
    n_invalid = rng.randint(5, 15)
    bad_positions = set(rng.sample(range(n_rows), n_invalid))

    rows = []
    for i in range(n_rows):
        name = rng.choice(FIRST_NAMES)
        row = {
            "user_id": f"u{shard_index}{i:04d}",
            "email": f"{name}{i}@{rng.choice(DOMAINS)}",
            "signup_date": f"2026-{rng.randint(1, 12):02d}-{rng.randint(1, 28):02d}",
            "country": rng.choice(COUNTRIES),
        }
        if i in bad_positions:
            row = corrupt(row, rng)
        rows.append(row)

    return rows, n_invalid


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", default="data")
    parser.add_argument("--shards", type=int, default=8)
    parser.add_argument("--n-rows", type=int, default=100)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    total = 0
    for i in range(args.shards):
        rows, n_invalid = generate(i, n_rows=args.n_rows, seed=args.seed)
        path = os.path.join(args.out_dir, f"shard_{i}.csv")
        with open(path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
        total += n_invalid
        print(f"Wrote {len(rows)} rows to {path} ({n_invalid} invalid)")

    print(f"Ground truth: {total} invalid rows across {args.shards} shards")


if __name__ == "__main__":
    main()
