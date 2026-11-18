"""Run from repository root with PYTHONPATH=src. Only modify temporary copies."""
import argparse
import json
import shutil
import tempfile
from pathlib import Path

from analysis.core import analyze, compare
from report.html import render


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("baseline", type=Path)
    parser.add_argument("current", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory() as tmp:
        summaries = []
        for label, source in (("baseline", args.baseline), ("current", args.current)):
            copy = Path(tmp) / label
            shutil.copytree(source, copy)
            for path in copy.glob("*/result.json"):
                row = json.loads(path.read_text(encoding="utf-8"))
                if row["quota_percent"] == 50 and not row["warmup"]:
                    (path.parent / "stdout.log").unlink()
            summaries.append(analyze(copy))
        history = compare(*summaries)
        rows = {row["quota_percent"]: row for row in history["comparisons"]}
        assert set(rows) == {None, 50, 100}
        assert rows[50]["verdict"] == "unable_to_compare" and rows[50]["wall_ratio"] is None
        assert (rows[50]["baseline_n"], rows[50]["current_n"]) == (0, 0)
        assert all(rows[q]["wall_ratio"] is not None for q in (None, 100))
        render(summaries[1], args.output, history)
        print(json.dumps(history, indent=2))


if __name__ == "__main__":
    main()
