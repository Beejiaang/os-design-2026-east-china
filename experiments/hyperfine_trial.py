"""One instrumented systemd trial, called repeatedly by hyperfine without a shell."""
import json
import sys
from pathlib import Path

from compare_tools import native_run


def main():
    batch = Path(sys.argv[1])
    request = json.loads((batch / "request.json").read_text())
    # Hyperfine invokes one command serially: retain warmup stdout too.
    index = len(list(batch.glob("trial-*")))
    directory = batch / f"trial-{index:03d}"
    row = native_run(request["config"], request["quota"], directory,
                     Path(request["time_binary"]))
    return 0 if row["status"] == "success" and row["cleanup_ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
