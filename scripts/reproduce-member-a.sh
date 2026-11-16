#!/usr/bin/env bash
# Preserve the clean checkout and all logs for inspection.
set -euo pipefail
repo=$(git -C "$(dirname "$0")" rev-parse --show-toplevel)
revision=$(git -C "$repo" rev-parse HEAD)
python_bin=${PYTHON:-python3}
output=${1:-"$repo/work/member-a-reproduction-$(date -u +%Y%m%dT%H%M%SZ)-$$"}
if [[ -e "$output" ]]; then
    echo "Output already exists: $output" >&2
    exit 2
fi
if [[ -n "$(git -C "$repo" status --porcelain)" ]]; then
    echo "Commit or preserve working-tree changes before reproducing HEAD" >&2
    exit 2
fi
mkdir -p "$output"
output=$(cd "$output" && pwd)
git clone --quiet --no-hardlinks --no-checkout "$repo" "$output/source"
git -C "$output/source" checkout --quiet --detach "$revision"
cd "$output/source"
export PYTHONPATH="$PWD/src"
printf '%s\n' "$revision" > "$output/commit.txt"
"$python_bin" -m runner doctor > "$output/doctor.json"
OSDESIGN_INTEGRATION=1 "$python_bin" -m unittest discover -s tests -v 2>&1 | tee "$output/tests.log"
"$python_bin" -m runner run examples/cpu.json --output "$output/experiment" | tee "$output/experiment.log"
if [[ -n "$(git status --porcelain)" ]]; then
    echo "Clean reproduction modified tracked/source files" >&2
    exit 1
fi
echo "Reproduction evidence: $output"
