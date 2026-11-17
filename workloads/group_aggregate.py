"""Single-process streaming integer group-by; deterministic output only."""
import argparse
import csv
import json


def aggregate(path):
    groups = {}
    rows = 0
    with open(path, newline="", encoding="utf-8") as stream:
        reader = csv.reader(stream)
        if next(reader, None) != ["group", "value"]:
            raise ValueError("Expected group,value header")
        for fields in reader:
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
    args = parser.parse_args()
    print(json.dumps(aggregate(args.input), separators=(",", ":")))
