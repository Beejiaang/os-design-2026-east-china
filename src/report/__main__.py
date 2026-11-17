import argparse
import json
import sys
from pathlib import Path

from analysis.core import analyze, compare
from report.html import render


def main():
    parser = argparse.ArgumentParser(description="Offline finalized-run analysis; never executes workloads")
    parser.add_argument("experiment", type=Path)
    parser.add_argument("--baseline", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        summary = analyze(args.experiment)
        comparison = compare(analyze(args.baseline), summary) if args.baseline else None
        render(summary, args.output, comparison)
        print(json.dumps({"complete": summary["complete"], "eligible": len(summary["eligible"]),
                          "excluded": len(summary["excluded"]), "issues": summary["issues"]}, ensure_ascii=False))
        return 0 if summary["complete"] and summary["eligible"] else 1
    except (OSError, ValueError, RuntimeError, ImportError) as exc:
        print(str(exc), file=sys.stderr)
        return 2


sys.exit(main())
