import argparse
import json
import sys
from pathlib import Path

from collector.system import doctor
from runner.core import experiment
from runner.compatibility import check_compatibility


def main():
    parser = argparse.ArgumentParser(description="CPU quota experiments (Linux/systemd user/cgroup v2)")
    commands = parser.add_subparsers(dest="action", required=True)
    commands.add_parser("doctor")
    run = commands.add_parser("run")
    run.add_argument("config", type=Path)
    run.add_argument("--output", type=Path, required=True)
    compare = commands.add_parser("check-compatibility", help="Check two result.json files; no performance verdict")
    compare.add_argument("baseline", type=Path)
    compare.add_argument("current", type=Path)
    args = parser.parse_args()
    try:
        if args.action == "doctor":
            result = doctor()
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0 if result["supported"] else 2
        if args.action == "check-compatibility":
            result = check_compatibility(json.loads(args.baseline.read_text(encoding="utf-8")),
                                         json.loads(args.current.read_text(encoding="utf-8")))
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0 if result["compatible"] else 1
        rows = experiment(json.loads(args.config.read_text(encoding="utf-8")), args.output)
        return 0 if rows and all(row["status"] == "success" for row in rows) else 1
    except (OSError, ValueError, RuntimeError) as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
