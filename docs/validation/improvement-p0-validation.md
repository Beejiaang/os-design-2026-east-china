# P0 改进验证（2026-11-17）

任务 1 目标机测量源码 d8a331e 及 54 次对照见[对照验证](comparison-validation.md#hyperfine-新增目标机验证任务-1)。本页补充 CI 与材料脚本（任务 6/8）的验证，源码固定 **a4f4c04**，由代理执行。

## openEuler 干净提交验证

从 bundle 新检出 /home/holo/projects/osdesign-improve-p0-20261117，Python 3.11.6，使用现有 osdesign-release-venv-20261117；离线安装 `.[dev]`、pip check 均成功，工作树验证前后干净。未修改资源设置。

```bash
python -m pip install --no-index --find-links ~/projects/repro-wheels-20261117 -e '.[dev]'
python -m pip check
PYTHONPATH=src OSDESIGN_INTEGRATION=0 python -m unittest discover -s tests -v
python scripts/validate_contracts.py examples/cpu.json --config
python scripts/validate_contracts.py examples/measured-run-1.1.json
PYTHONPATH=src OSDESIGN_INTEGRATION=1 python -m unittest discover -s tests -v
python experiments/run_pipeline.py --output results/pipeline
python scripts/material_manifest.py --output work/materials.md
sha256sum work/materials.md
```

实际 python 为 ~/projects/osdesign-release-venv-20261117/bin/python。纯测试 29 项中 20 通过、9 项系统测试跳过；全量 29 项通过、0 跳过。完整流程 18 份最终记录、15 条有效测量（3 条预热排除），重新 analyze() 完整性/正确性证据通过。结束时 osdesign-* 用户单元为零。

材料表连续生成两次，SHA256 一致。原始 session、两份测试日志、默认 pipeline 全部输出及材料表在[目标机归档](../../evidence/improvement/improve-p0-openeuler-20261117.tar.gz)，[哈希清单](../../evidence/improvement/SHA256SUMS)。CSV 排除，可用 input.json 固定参数复建。

## 本地 Python 3.12 与 CI 范围

Windows CPython 3.12.14，新建 work/ci312 venv，安装 `.[dev]`，执行相同 pip check、纯 unittest 与两个 validate_contracts 命令。依赖和 schema 通过；29 项中20通过、9项按门控跳过。[测试日志](../../evidence/improvement/p0-windows-python312-tests.log)。不得将其描述为 Ubuntu 3.12 或目标机系统测试。

CI 配置 ubuntu-latest × Python 3.11/3.12，只执行纯单测与 schema，保留既有集成门控，不改测试语义。无推送授权，**GitHub Actions 实际尚未运行**；上述为手动等价命令验证，未声称验证了 GitHub 服务或两版 Ubuntu 矩阵。ruff 尚未接入，任务17完成后再启用。

## 材料漂移与文档检查

[临时夹具检查](../../evidence/improvement/check-manifest-drift.py)在临时目录构造错误哈希，生成器明确拒绝；未修改真实冻结二进制。所有现有 evidence SHA256SUMS、release-manifest 三个声明哈希与本地 Markdown 链接检查通过。生成表记录的是生成时 HEAD 和路径最近内容提交，不能替代实验源码版本或宣称 RC1 PDF/PPT 已同步最新实验。

上述是代理实测和检查，不是人员交叉验收、官方提交、统计准确率或教学效果验收。
