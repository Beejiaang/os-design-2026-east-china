"""Bind current material bytes to Git provenance; reject drift from RC1 hashes."""
import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT).decode("utf-8").strip()


def generate(output):
    manifest_path = ROOT / "demo/delivery/release-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    declared = manifest["files"]
    paths = set(declared)
    paths.update(p.relative_to(ROOT).as_posix() for p in (ROOT / "evidence").rglob("*.tar.gz"))
    paths.update(["docs/implementation/design-and-test-report.md",
                  "docs/implementation/teaching-experiments.md"])
    tracked = set(git("ls-files", "-z").split("\0"))
    # Exclude this generated file so rerunning does not change its own status.
    changed = set(git("diff", "HEAD", "--name-only", "-z").split("\0")) - {""}
    untracked = set(git("ls-files", "--others", "--exclude-standard", "-z").split("\0")) - {""}
    relative_output = output.relative_to(ROOT).as_posix() if output.is_relative_to(ROOT) else None
    changed.discard(relative_output)
    untracked.discard(relative_output)
    rows = []
    for name in sorted(paths):
        path = (ROOT / name).resolve()
        if not path.is_relative_to(ROOT):
            raise ValueError("Manifest path escapes repository: " + name)
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if name in declared and declared[name] != digest:
            raise ValueError("RC1 material hash mismatch: " + name)
        content_commit = git("log", "-1", "--format=%H", "--", name) if name in tracked else "untracked"
        status = "dirty" if name in changed else "untracked" if name in untracked else "committed"
        link = quote(Path(os.path.relpath(path, output.parent)).as_posix(), safe="/.")
        rows.append(f"| [{name}]({link}) | `{content_commit}` | {status} | `{digest}` |")
    text = ("# 材料、版本与 SHA256 对应表\n\n"
            f"生成时 Git HEAD：`{git('rev-parse', 'HEAD')}`；分支：`{git('branch', '--show-current')}`。\n\n"
            f"生成时除本表外的改动路径：{json.dumps(sorted(changed | untracked), ensure_ascii=False)}。\n\n"
            f"RC1 声明实现快照：`{manifest['implementation_snapshot']}`；测量来源："
            f"`{', '.join(manifest['measurement_sources'])}`；分析来源：`{manifest['analysis_source']}`。\n\n"
            "内容提交列为该路径最近一次 Git 提交，**不是实验执行源码提交**；实验源码以对应验证记录为准。"
            "哈希为当前磁盘字节，RC1 已声明三份二进制材料须匹配冻结清单；"
            "正文、教学稿和新证据可以晚于 RC1，不因此认定 PDF/PPT 已更新。\n\n"
            "| 材料 | 路径最近内容提交 | 当前状态 | SHA256 |\n|---|---|---|---|\n"
            + "\n".join(rows) + "\n\n"
            "重跑：`python scripts/material_manifest.py --output docs/validation/material-versions.md`。"
            "同一 Git 状态与材料字节下输出确定；提交变化后重新生成会记录新 HEAD。"
            "旧归档和 release-manifest.json 不自动改写；不代表人工验收或正式提交。\n")
    return text


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    content = generate(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(content, encoding="utf-8", newline="\n")
    print("Wrote " + str(output))


if __name__ == "__main__":
    main()
