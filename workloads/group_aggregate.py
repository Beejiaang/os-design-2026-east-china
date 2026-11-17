"""Single-process streaming integer group-by; deterministic output only."""
import argparse
import csv
import json
from itertools import islice


def aggregate(path, limit=None):
    groups = {}
    rows = 0
    with open(path, newline="", encoding="utf-8") as stream:
        reader = csv.reader(stream)
        if next(reader, None) != ["group", "value"]:
            raise ValueError("Expected group,value header")
        for fields in islice(reader, limit):
            if len(fields) != 2:
                raise ValueError("Expected two columns")
            key, value = map(int, fields)
            if key < 0:
                raise ValueError("Group must be nonnegative")
            count, total = groups.get(key, (0, 0))
            groups[key] = count + 1, total + value
            rows += 1
    return {"rows": rows, "groups": [[key, *groups[key]] for key in sorted(groups)]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("--passes", type=int, choices=range(1, 5), default=1,
                        help="Controlled extra full passes for known-slow validation")
    parser.add_argument("--extra-percent", type=int, choices=range(101), default=0,
                        help="Controlled additional partial pass, output unchanged")
    args = parser.parse_args()
    for _ in range(args.passes):
        result = aggregate(args.input)
    if args.extra_percent:
        aggregate(args.input, max(1, result["rows"] * args.extra_percent // 100))
    print(json.dumps(result, separators=(",", ":")))
