"""Conservative preconditions for C's historical comparison; no regression verdict."""
import math


def check_compatibility(baseline, current):
    reasons = []
    for name, row in (("baseline", baseline), ("current", current)):
        if row.get("source") != "measured" or row.get("status") != "success" or not row.get("cleanup_ok"):
            reasons.append(name + ": requires successful measured run with verified cleanup")
        if row.get("warmup"):
            reasons.append(name + ": warmup is excluded")
        if not row.get("quota_verified"):
            reasons.append(name + ": quota was not verified")
        if not row.get("environment", {}).get("fingerprint") or not row.get("stdout_sha256"):
            reasons.append(name + ": compatibility evidence missing")
        if row.get("schema_version") != "1.0":
            reasons.append(name + ": unsupported schema")
        for field in ("input_id", "workload_version", "runner_sha256"):
            if not isinstance(row.get(field), str) or not row[field]:
                reasons.append(name + ": missing " + field)
        for field in ("wall_seconds", "cpu_seconds"):
            if type(row.get(field)) not in (int, float) or not math.isfinite(row[field]) or row[field] < 0:
                reasons.append(name + ": missing/invalid " + field)
    for key in ("input_id", "quota_percent", "timeout_seconds", "stdout_sha256", "runner_sha256"):
        if baseline.get(key) != current.get(key):
            reasons.append(key + " differs")
    if baseline.get("environment", {}).get("fingerprint") != current.get("environment", {}).get("fingerprint"):
        reasons.append("environment fingerprint differs")
    # Drop each run's unique leaf directory while retaining actual service ancestors.
    for name, row in (("baseline", baseline), ("current", current)):
        if not row.get("visible_limits"):
            reasons.append(name + ": actual service hierarchy missing")
    if baseline.get("visible_limits", [])[1:] != current.get("visible_limits", [])[1:]:
        reasons.append("actual service parent limits differ")
    return {"compatible": not reasons, "reasons": reasons,
            "note": "Preconditions only. Statistical analysis and workload-specific correctness belong to B/C."}
