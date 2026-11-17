#!/bin/bash
set -euo pipefail
repo=/home/holo/projects/osdesign-release-20261117
venv=/home/holo/projects/osdesign-release-venv-20261117
test ! -e "$repo"
test ! -e "$venv"
git clone --branch feat/a-release-preparation /home/holo/projects/release-rc1.bundle "$repo"
cd "$repo"
mkdir -p work/release-validation
exec >work/release-validation/session.log 2>&1
date --iso-8601=seconds
git rev-parse HEAD
git status --porcelain
uname -a
cat /etc/os-release
python3 -m venv "$venv"
export PIP_NO_INDEX=1
export PIP_FIND_LINKS=/home/holo/projects/repro-wheels-20261117
"$venv/bin/python" -m pip install -e '.[report]'
"$venv/bin/python" -m pip check
"$venv/bin/python" -m pip freeze >work/release-validation/requirements.txt
export PYTHONPATH="$repo/src"
"$venv/bin/python" -m runner doctor >work/release-validation/doctor.json
OSDESIGN_INTEGRATION=1 "$venv/bin/python" -m unittest discover -s tests -v >work/release-validation/tests.log 2>&1
"$venv/bin/python" experiments/run_pipeline.py --output results/release >work/release-validation/pipeline.log 2>&1
"$venv/bin/python" -m report results/release/experiment --output results/release/recomputed.html >work/release-validation/report.log 2>&1
systemctl --user list-units 'osdesign-*' --all --no-pager >work/release-validation/units-after.txt
git rev-parse HEAD
git status --porcelain
date --iso-8601=seconds
tar --exclude='results/release/input.csv' -czf /home/holo/projects/release-openeuler-20261117.tar.gz work/release-validation results/release
tail -5 work/release-validation/tests.log
