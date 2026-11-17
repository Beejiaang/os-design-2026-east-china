set -euo pipefail
cd /home/holo/projects/osdesign-p1-20261117
venv=/home/holo/projects/osdesign-p1-venv-20261117
git fetch /home/holo/projects/p1-final-code.bundle improve/10-scale-sweep
git checkout --detach FETCH_HEAD
mkdir -p work/p1-validation/task10
exec >work/p1-validation/task10/session.log 2>&1
git rev-parse HEAD
test -z "$(git status --porcelain)"
export PYTHONPATH="$PWD/src"
"$venv/bin/python" -m pip check
"$venv/bin/python" -m ruff check src workloads experiments tests scripts
OSDESIGN_INTEGRATION=1 "$venv/bin/python" -m unittest discover -s tests -v >work/p1-validation/task10/tests.log 2>&1
"$venv/bin/python" experiments/run_pipeline.py --output results/p1/task10 >work/p1-validation/task10/pipeline.log 2>&1
"$venv/bin/python" experiments/scale_sweep.py --output results/scale-sweep --time-binary /home/holo/projects/comparison-tools/time-install/bin/time >work/p1-validation/task10/scale.log 2>&1
systemctl --user list-units 'osdesign-*' --all --no-pager >work/p1-validation/task10/units-after.txt
test -z "$(git status --porcelain)"
tar --exclude=input.csv -czf /home/holo/projects/p1-final-openeuler-20261117.tar.gz work/p1-validation/task10 results/p1/task10 results/scale-sweep
