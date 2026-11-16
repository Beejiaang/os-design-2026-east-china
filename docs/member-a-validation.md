# 成员 A 验证记录

日期：2026-11-16，北京时间。代理通过 SSH 真实运行；非实现者独立复现未完成。

## 环境

- openEuler 24.03 LTS-SP4，x86_64，Hyper-V 虚拟机
- 内核 6.6.0-159.4.3.154.oe2403sp4.x86_64，4 个逻辑 CPU，来宾报告 Intel Core i5-14600KF
- Python 3.11.6，项目既有虚拟环境 `~/projects/osdesign-venv`
- cgroup v2，systemd 用户管理器，普通用户执行
- 当前工作基于文档提交 e8f27bd，实验时新增代码尚未提交；原始记录包含 git_dirty 和 runner_sha256，不能将该文档提交当成已含本次代码

## 自动检查

`PYTHONPATH=src OSDESIGN_INTEGRATION=1 ~/projects/osdesign-venv/bin/python -m unittest discover -s tests -v`

8 项测试全部通过，最后一次记录用时 2.819 秒：配置和非法配额校验、缺失指标保留 null、基线兼容门槛、任务退出 7、命令不存在、三档配额各两次和相同输出、超时及另建会话的 sleep 子进程清理。

此前在 Ubuntu 26.04.1 / WSL2 / Python 3.14.4 也运行过同一核心测试；首轮发现无配额叶节点未启用 CPU 控制器时 `cpu.max` 缺失，修正后 8 项通过。WSL 结果只作为兼容补充，不混入 openEuler 性能数据。

## 三档真实实验

命令：`PYTHONPATH=src ~/projects/osdesign-venv/bin/python -m runner run examples/cpu.json --output results/member-a-openeuler-20261116`

配置：1,500,000 次 SHA256 固定链计算；未设置本地配额、100%、50% 三档；每档预热 1 次、正式 3 次；顺序种子 20261116；单次超时 30 秒。

| 配额 | 正式样本数 | wall_seconds 中位数 | cpu_seconds 中位数 | 正式样本 nr_throttled |
|---|---:|---:|---:|---|
| 未设置本地配额 | 3 | 0.464844 | 0.416678 | null（叶节点未启用 CPU 带宽控制器） |
| 100% | 3 | 0.464932 | 0.412502 | 0、0、0 |
| 50% | 3 | 0.815711 | 0.412435 | 8、8、8 |

全部 12 次 status=success、quota_verified=true、cleanup_ok=true，标准输出 SHA256 一致。成功样本不包含异常测试，异常测试单独核验预期失败状态。样本少且探针短，上表仅展示配额行为和接口工作，不宣称显著性、诊断准确率或真实数据任务性能提升。

## 证据

仓库内归档：[`evidence/member-a/openeuler-20261116.tar.gz`](../evidence/member-a/openeuler-20261116.tar.gz)，校验值见同目录 `SHA256SUMS`。包含完整实验目录（配置、环境、JSONL、CSV、每次测量、stdout/stderr、清理结果）及 `member-a-tests.log`。可解压至独立目录后按 run_id 追溯：

```bash
mkdir -p work/member-a-evidence
tar -xzf evidence/member-a/openeuler-20261116.tar.gz -C work/member-a-evidence
```

未压缩数据也保留在本机和虚拟机的 `results/member-a-openeuler-20261116`。该探针生成的输出为计算哈希；归档不包含 SSH 密钥、访问凭据或完整私人聊天。

## 待队友完成的验收

B 接入可校验分组聚合任务并交叉检查 A；C 接入真实结果、分布、报告和历史回归分析。A 再核对 C 的报告与原始记录一致性。非实现者独立复现、统计判定规则和最终赛事提交仍未完成。本记录不替代整个项目验收。

## 第二步：兼容接口与干净源码复验

同日继续按 12/06 的 A 范围推进。实现提交 `02f5c650da9595367a8134330371d9a2e167e055`：补齐无效/缺失记录的拒绝条件、严格状态与指标校验、命令行 `check-compatibility`，增加干净源码复验脚本。

在 openEuler 执行：

```bash
PYTHON=~/projects/osdesign-venv/bin/python bash scripts/reproduce-member-a.sh work/member-a-stage2-20261116
```

脚本独立检出上述提交，9 项测试在 2.888 秒内全部通过，新一轮三档共 12 次实验全部成功，输出一致、配额核验和清理均通过；每条实验的 git_commit 均为上述提交，git_dirty 为空，检出源码运行前后保持干净。没有残留 `osdesign-*.service` 单元。

兼容 CLI 另做 7 类检查：同条件真实样本退出 0；不同配额、环境为 null、层级为 null、timeout 状态、非对象记录退出 1；损坏 JSON 退出 2。全部符合预期，无 traceback。故障输入是注入的测试夹具，不作为真实性能样本。

新增证据：[stage2-openeuler-20261116.tar.gz](../evidence/member-a/stage2-openeuler-20261116.tar.gz)，同目录 SHA256SUMS 覆盖两份归档。包含提交号、预检、测试日志、完整新实验及兼容命令检查报告；不包含检出的 `.git` 或故障夹具原文件。

此轮推进了 A 的基线前提接口和复验能力。B/C 联调、队友独立复现及统计回归判定仍保持待验收。

## 第三步：中断、崩溃、恢复与协作规则

源代码提交：`9c075aa9031ea3b699dbf22b1b2bd7d9b94f38b4`。在 openEuler 从该干净提交独立检出，运行 `scripts/reproduce-member-a.sh work/member-a-stage3-20261116`。

- 17 项测试全部通过，9.089 秒；其中真实系统项覆盖 SIGINT、SIGTERM、中间快照损坏、worker SIGKILL、执行器 SIGKILL 后看门狗与恢复、脱离会话的后代清理、活跃执行器恢复拒绝和跨启动恢复拒绝。
- 用户管理器不可用、预检权限失败、配置拼写错误的测试使用明确的故障模拟，不声称实际撤销系统权限。
- 初轮新测试发现 RemainAfterExit 服务进入 active/exited 后运行时限不足以兜底，改为 worker 在测量后保持运行，直到正常回收或看门狗终止；修正后复验通过。初轮失败日志没有作为通过证据。
- 新一轮 12 次三档实验全部 success，quota_verified/cleanup_ok 全为 true，输出哈希一致，schema_version 全为 1.1，git_dirty 全为空。实验 manifest 为 complete、planned_count=12、finalized_count=12、pending_count=0。
- 保留 5 份故障注入最终记录：SIGINT、SIGTERM、损坏开始快照三份 interrupted，worker 崩溃一份 error，强制丢失执行器并恢复一份 aborted；都不进入性能样本。
- 使用可选 jsonschema 开发工具验证 12 份正常记录和 5 份异常最终记录均符合 run-1.1；配置示例符合 config-1.0。恢复 CLI 对已恢复目录再次执行返回 complete=true、checks=[]，未重复改写记录。
- 最终检查无残留 `osdesign-*.service`，主工作目录和干净检出均无源码改动。

证据：[stage3-openeuler-20261116.tar.gz](../evidence/member-a/stage3-openeuler-20261116.tar.gz)，包含提交号、预检、测试日志、12 次完整实验及单独标注的故障注入目录；校验值在 SHA256SUMS。[measured-run-1.1.json](../examples/measured-run-1.1.json) 是其中一个未经改写的正式样本快照，artifacts 的相对路径指向归档中原实验目录，并非 examples 目录。

已增加 AGENTS.md、统一口径、数据协议、A/B/C 启动任务和交接模板。协议升级 1.1 并保留原 1.0 归档；兼容检查要求同版及干净 Git 证据。B/C 联调、人员交叉复现、统计规则、PR 合并和官方提交仍需对应证据，不能从本轮通过结果推定完成。
