"""Best-effort Linux load evidence, separate from compatibility and verdicts."""
import json
import math
import threading
import time
from datetime import datetime, timezone
from pathlib import Path


class HostLoadSampler:
    def __init__(self, directory, interval=5.0):
        if not math.isfinite(interval) or interval <= 0:
            raise ValueError("Load sampling interval must be positive")
        self.path = Path(directory) / "host-load.jsonl"
        self.interval = interval
        self.stop = threading.Event()
        self.thread = None
        self.samples = 0
        self.errors = []

    def sample(self):
        row = {"kind": "linux-load-v1", "timestamp_utc": datetime.now(timezone.utc).isoformat(),
               "monotonic_seconds": time.monotonic(), "loadavg": None, "raw": None, "error": None}
        try:
            row["raw"] = Path("/proc/loadavg").read_text().strip()
            values = [float(value) for value in row["raw"].split()[:3]]
            if len(values) != 3 or any(not math.isfinite(value) or value < 0 for value in values):
                raise ValueError("Invalid /proc/loadavg")
            row["loadavg"] = values
        except (OSError, ValueError) as exc:
            row["error"] = str(exc)
            self.errors.append(str(exc))
        try:
            with self.path.open("a", encoding="utf-8") as stream:
                stream.write(json.dumps(row) + "\n")
            self.samples += 1
        except OSError as exc:
            self.errors.append(str(exc))

    def loop(self):
        while not self.stop.wait(self.interval):
            self.sample()

    def __enter__(self):
        self.sample()
        self.thread = threading.Thread(target=self.loop, name="osdesign-load-evidence", daemon=True)
        self.thread.start()
        return self

    def __exit__(self, *exc):
        self.stop.set()
        self.thread.join()
        self.sample()

    def metadata(self):
        return {"kind": "linux-load-v1", "path": self.path.name, "interval_seconds": self.interval,
                "samples": self.samples, "errors": self.errors,
                "note": "Executing Linux environment; not necessarily the physical hypervisor host. Not a verdict input."}
