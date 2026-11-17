set -euo pipefail
repo=/home/holo/projects/osdesign-p1-20261117
venv=/home/holo/projects/osdesign-p1-venv-20261117
git clone --branch improve/10-scale-sweep /home/holo/projects/p1-stage.bundle "$repo"
python3 -m venv "$venv"
cd "$repo"
export PIP_NO_INDEX=1
export PIP_FIND_LINKS=/home/holo/projects/repro-wheels-20261117
export PYTHONPATH="$repo/src"
mkdir -p work/p1-validation
exec >work/p1-validation/session.log 2>&1
for pair in task17:f96e456 task18:5e0a9d9 task11:1bde76a task13:2d60a88 task14:0be73a7; do
 name=${pair%%:*}
 revision=${pair##*:}
 git checkout --detach "$revision"
 mkdir -p work/p1-validation/"$name"
 git rev-parse HEAD >work/p1-validation/"$name"/commit.txt
 test -z "$(git status --porcelain)"
 "$venv/bin/python" -m pip install -e '.[dev]' >work/p1-validation/"$name"/install.log 2>&1
 "$venv/bin/python" -m pip check >work/p1-validation/"$name"/pip-check.log
 "$venv/bin/python" -m ruff check src workloads experiments tests scripts >work/p1-validation/"$name"/ruff.log
 OSDESIGN_INTEGRATION=1 "$venv/bin/python" -m unittest discover -s tests -v >work/p1-validation/"$name"/tests.log 2>&1
 "$venv/bin/python" experiments/run_pipeline.py --output results/p1/"$name" >work/p1-validation/"$name"/pipeline.log 2>&1
 "$venv/bin/python" -c 'from pathlib import Path; import sys; from analysis.core import analyze; s=analyze(Path(sys.argv[1])); assert s["complete"] and s["finalized_count"]==18 and len(s["eligible"])==15; print("18 final records, 15 eligible verified")' results/p1/"$name"/experiment >work/p1-validation/"$name"/independent-check.log
 "$venv/bin/python" scripts/validate_contracts.py results/p1/"$name"/experiment/runs.jsonl >work/p1-validation/"$name"/schema.log
 systemctl --user list-units 'osdesign-*' --all --no-pager >work/p1-validation/"$name"/units-after.txt
 test -z "$(git status --porcelain)"
 echo "$name validated $revision"
done
"$venv/bin/python" -m pip freeze >work/p1-validation/requirements.txt
uname -a >work/p1-validation/uname.txt
cat /etc/os-release >work/p1-validation/os-release.txt
tar --exclude=input.csv -czf /home/holo/projects/p1-staged-openeuler-20261117.tar.gz work/p1-validation results/p1
