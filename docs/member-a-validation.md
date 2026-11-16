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
