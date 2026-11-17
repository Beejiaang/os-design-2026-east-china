"""Package a committed source snapshot, its Git history and optional wheels.

No working files, credentials, results or recursive ZIPs are collected. A clean
worktree and a named source branch are required. The manifest binds each byte
to the source commit; this is a candidate package, not a submission receipt.
"""
import argparse
import hashlib
import io
import json
import subprocess
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED


def git(*args):
    return subprocess.check_output(["git", *args])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--wheels", type=Path)
    parser.add_argument("--label", choices=("RC1", "RC2"), default="RC1")
    args = parser.parse_args()
    if git("status", "--porcelain").strip():
        parser.error("commit the reviewed changes before packaging")
    branch = git("symbolic-ref", "--quiet", "HEAD").decode().strip()
    commit = git("rev-parse", "HEAD").decode().strip()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.exists():
        parser.error("output already exists")
    bundle = args.output.parent / ("project-" + commit[:12] + ".bundle")
    if bundle.exists():
        parser.error("bundle already exists")
    git("bundle", "create", str(bundle.resolve()), branch)
    files = {bundle.name: bundle.read_bytes()}
    with ZipFile(io.BytesIO(git("archive", "--format=zip", "HEAD"))) as source:
        for name in source.namelist():
            if not name.endswith(("/", ".zip", ".bundle")):
                files["project/" + name] = source.read(name)
    if args.wheels:
        for path in sorted(args.wheels.glob("*.whl")):
            files["wheels/" + path.name] = path.read_bytes()
    files["README.txt"] = (
        "候选交付 " + args.label + "，未人工验收，未含正式视频或赛事接收凭据\n"
        "源码提交 " + commit + "\n"
        "运行：先读 project/README.md 与 project/docs/validation/peer-reproduction.md\n"
        "源码快照可直接检出运行，Git 历史可用 git clone 包内 bundle 文件恢复\n"
        "wheels 仅对应 Linux x86_64 CPython 3.11，不配置系统权限\n"
        "离线安装：在 project 目录执行 python3 -m pip install --no-index --find-links ../wheels -e '.[report]'\n"
        "文件完整性：核对 MANIFEST.json 中各文件 SHA256；哈希不证明正式提交或人工验收\n"
    ).encode("utf-8")
    manifest = {"kind": "osdesign-candidate-release-v1", "release_label": args.label, "source_commit": commit,
                "source_ref": branch, "human_acceptance": "excluded_pending",
                "video": "excluded_pending", "competition_submission": "not_confirmed",
                "files": {n: hashlib.sha256(data).hexdigest() for n, data in sorted(files.items())}}
    with ZipFile(args.output, "x", ZIP_DEFLATED) as output:
        for name, data in sorted(files.items()):
            output.writestr(name, data)
        output.writestr("MANIFEST.json", json.dumps(manifest, ensure_ascii=False, indent=2))
    with ZipFile(args.output) as output:
        assert output.testzip() is None
        for name, expected in manifest["files"].items():
            assert hashlib.sha256(output.read(name)).hexdigest() == expected, name
    checksum = hashlib.sha256(args.output.read_bytes()).hexdigest()
    args.output.with_suffix(".zip.sha256").write_text(checksum + "  " + args.output.name + "\n", encoding="utf-8")
    print(json.dumps({"path": str(args.output), "source_commit": commit,
                      "files": len(files), "sha256": checksum, "bytes": args.output.stat().st_size}))


if __name__ == "__main__":
    main()
