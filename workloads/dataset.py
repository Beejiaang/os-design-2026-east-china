"""Portable fixed-seed input and independent SQLite reference (outside timing)."""
import csv
import hashlib
import json
import sqlite3
from pathlib import Path


def sha256(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def generate(path, rows, groups, seed):
    if type(rows) is not int or rows < 1 or type(groups) is not int or groups < 1:
        raise ValueError("rows and groups must be positive integers")
    if type(seed) is not int or not 0 <= seed < 2**32:
        raise ValueError("seed must be a uint32")
    state = seed
    with Path(path).open("x", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(["group", "value"])
        for _ in range(rows):
            state = (1664525 * state + 1013904223) % 2**32
            key = (state >> 8) % groups
            state = (1664525 * state + 1013904223) % 2**32
            writer.writerow([key, state % 20001 - 10000])
    return {"generator": "lcg32-csv-v1", "rows": rows, "groups_requested": groups,
            "seed": seed, "sha256": sha256(path)}


def reference(path):
    # Different implementation: SQLite GROUP BY, no import of the workload.
    # Integer input bounds keep sums within signed 64-bit for supported sizes.
    with sqlite3.connect(":memory:") as db:
        db.execute("CREATE TABLE data (g INTEGER, v INTEGER)")
        with Path(path).open(newline="", encoding="utf-8") as stream:
            reader = csv.reader(stream)
            if next(reader, None) != ["group", "value"]:
                raise ValueError("Expected group,value header")
            def records():
                for fields in reader:
                    if len(fields) != 2:
                        raise ValueError("Expected two columns")
                    key, value = map(int, fields)
                    if key < 0 or not -10000 <= value <= 10000:
                        raise ValueError("Input outside reference bounds")
                    yield key, value
            db.executemany("INSERT INTO data VALUES (?, ?)", records())
        return {"rows": db.execute("SELECT COUNT(*) FROM data").fetchone()[0],
                "groups": [list(row) for row in db.execute(
                    "SELECT g, COUNT(*), SUM(v) FROM data GROUP BY g ORDER BY g")]}


def check_output(path, expected):
    # Compare the exact deterministic serialization, rejecting duplicate keys,
    # bool-as-int, extra text, reordered groups and all altered values.
    canonical = (json.dumps(expected, separators=(",", ":")) + "\n").encode()
    return Path(path).read_bytes() == canonical
