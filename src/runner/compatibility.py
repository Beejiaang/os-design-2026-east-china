"""Conservative preconditions for C's historical comparison; no regression verdict."""
import math
import re


from collector.system import environment_fingerprint


def login_environment(env):
    """Compare verified login snapshots while retaining every measured limit."""
    if not isinstance(env, dict):
        return None
    fields = dict(env)
    fingerprint = fields.pop("fingerprint", None)
    limits = fields.get("visible_limits")
    if (not isinstance(limits, list) or len(limits) < 2 or
            not all(isinstance(entry, dict) for entry in limits) or
            not re.fullmatch(r"[0-9a-f]{64}", str(fields.get("machine_id_sha256"))) or
            fingerprint != environment_fingerprint(fields)):
        return None
    leaf = limits[0]
    match = re.fullmatch(r"(/sys/fs/cgroup/user[.]slice/user-[0-9]+[.]slice)/session-[0-9]+[.]scope",
                         str(leaf.get("path")))
    if (not match or limits[1].get("path") != match[1] or
            not isinstance(leaf.get("cpu_max"), str) or "cpuset_effective" not in leaf):
        return None
    fields["visible_limits"] = [dict(leaf, path=match[1] + "/session-*.scope"), *limits[1:]]
    return fields


def check_compatibility(baseline, current):
    reasons = []
    if not isinstance(baseline, dict) or not isinstance(current, dict):
        return {"compatible": False, "reasons": ["Each input must be a run object"],
                "note": "Preconditions only; no regression verdict."}
    for name, row in (("baseline", baseline), ("current", current)):
        if row.get("source") != "measured" or row.get("status") != "success" or row.get("cleanup_ok") is not True:
            reasons.append(name + ": requires successful measured run with verified cleanup")
        if row.get("warmup") is not False:
            reasons.append(name + ": explicit non-warmup run required")
        if row.get("quota_verified") is not True:
            reasons.append(name + ": quota was not verified")
        env = row.get("environment")
        if not isinstance(env, dict) or not isinstance(env.get("fingerprint"), str) or not env["fingerprint"]:
            reasons.append(name + ": compatibility evidence missing")
        if not isinstance(row.get("stdout_sha256"), str) or not row["stdout_sha256"]:
            reasons.append(name + ": output evidence missing")
        if row.get("schema_version") not in ("1.0", "1.1"):
            reasons.append(name + ": unsupported schema")
        for field in ("input_id", "workload_version", "runner_sha256"):
            if not isinstance(row.get(field), str) or not row[field]:
                reasons.append(name + ": missing " + field)
        if not isinstance(row.get("git_commit"), str) or not re.fullmatch(r"[0-9a-f]{40}", row["git_commit"]) or row.get("git_dirty") != "":
            reasons.append(name + ": clean, identifiable code revision required")
        for field in ("wall_seconds", "cpu_seconds"):
            if type(row.get(field)) not in (int, float) or not math.isfinite(row[field]) or row[field] < 0:
                reasons.append(name + ": missing/invalid " + field)
        if type(row.get("exit_code")) is not int or row["exit_code"] != 0:
            reasons.append(name + ": successful exit code required")
        if type(row.get("timeout_seconds")) not in (int, float) or not math.isfinite(row["timeout_seconds"]) or row["timeout_seconds"] <= 0:
            reasons.append(name + ": invalid timeout")
        quota = row.get("quota_percent")
        if "quota_percent" not in row or (quota is not None and
                (type(quota) not in (int, float) or not math.isfinite(quota) or not 1 <= quota <= 10000)):
            reasons.append(name + ": missing/invalid quota")
        delta = row.get("cpu_stat_delta")
        if not isinstance(delta, dict) or type(delta.get("usage_usec")) is not int or delta["usage_usec"] < 0:
            reasons.append(name + ": cgroup CPU usage evidence missing/invalid")
    for key in ("schema_version", "input_id", "quota_percent", "timeout_seconds", "stdout_sha256", "runner_sha256"):
        if baseline.get(key) != current.get(key):
            reasons.append(key + " differs")
    if baseline.get("environment") != current.get("environment"):
        old_login = login_environment(baseline.get("environment"))
        if old_login is None or old_login != login_environment(current.get("environment")):
            reasons.append("environment metadata differs")
    # Drop each run's unique leaf directory while retaining actual service ancestors.
    for name, row in (("baseline", baseline), ("current", current)):
        hierarchy = row.get("visible_limits")
        if not isinstance(hierarchy, list) or len(hierarchy) < 2 or any(
                not isinstance(entry, dict) or not isinstance(entry.get("path"), str) or
                "cpu_max" not in entry or "cpuset_effective" not in entry for entry in hierarchy):
            reasons.append(name + ": actual service hierarchy missing")
    old_limits = baseline.get("visible_limits")
    new_limits = current.get("visible_limits")
    if isinstance(old_limits, list) and isinstance(new_limits, list) and old_limits[1:] != new_limits[1:]:
        reasons.append("actual service parent limits differ")
    return {"compatible": not reasons, "reasons": reasons,
            "note": "Preconditions only. Statistical analysis and workload-specific correctness belong to B/C."}
