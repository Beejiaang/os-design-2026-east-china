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
    parser.add_argument("--label", choices=("RC1", "RC2", "RC3"), default="RC1")
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
    install = "python -m pip install -e '.[report]'"
    if args.wheels:
        if not any(name.startswith("wheels/") for name in files):
            parser.error("the requested wheels directory contains no wheel files")
        install = 'PIP_NO_INDEX=1 PIP_FIND_LINKS="$PWD/../wheels" ' + install
    files["README.txt"] = (
        f"工程复验包 {args.label} · 源码 {commit}\n"
        "从解压目录开始，在 openEuler x86_64、CPython 3.11 和可用的 systemd 用户会话中执行。\n"
        "project/ 供阅读；下面的命令从包内 Git 历史检出源码，以便记录真实提交。\n"
        "请在新目录解压。完成后打开 review/results/first/report.html。\n"
        "\n```bash\n"
        "set -eu\n"
        f"git clone --branch {branch.removeprefix('refs/heads/')} ./{bundle.name} review\n"
        "cd review\n"
        f'test "$(git rev-parse HEAD)" = "{commit}"\n'
        "python3 -m venv .venv\n"
        ". .venv/bin/activate\n"
        f"{install}\n"
        "python -m pip check\n"
        "python -m runner doctor\n"
        "OSDESIGN_INTEGRATION=1 python -m unittest discover -s tests -v\n"
        "python experiments/run_pipeline.py --output results/first\n"
        'test -z "$(git status --porcelain)"\n'
        "```\n\n"
        "随包报告和幻灯片的版本见 project/demo/delivery/README.md。"
        "人员验收、正式视频与赛事接收状态见项目提交清单。\n"
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
