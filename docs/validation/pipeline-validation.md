# 聚合、分析与报告集成验证

日期：2026-11-17，Asia/Shanghai。由同一代理实际执行，不算非实现者或队友交叉验收。

## 源码与环境

- 本地开发分支：`feat/bc-end-to-end`，基于 A 集成分支 `a0d6edd`；保留原 A 工程与历史。
- 负载测量源码提交：`2ac22b71b43a9effefeedd550230347873bec38a`。最终分析修正提交：`1028dd8`（修复元数据为数组时的异常处理）；在此提交重算同一批原始记录并重跑测试，没有重标或改写原始测量的 Git 提交。
- openEuler 24.03 LTS-SP4 / x86_64 / 内核 `6.6.0-159.4.3.154.oe2403sp4.x86_64` / Python 3.11.6 / 4 vCPU；从 Git bundle 独立干净检出到 `/home/holo/projects/osdesign-integration-20261117`，没有覆盖原来的 A 开发目录。
- Ubuntu 26.04.1 WSL / 内核 `6.18.58.1-microsoft-standard-WSL2` / Python 3.14.4：另在 `/home/holo/osdesign-bc-20261117` 干净检出验证。两环境性能数据分别保存、不混作基线。
- Windows Python 3.13.9：普通测试 24 项中 15 通过、9 项系统测试按预期跳过；不当作目标系统测试通过。
- 分析使用 jsonschema。openEuler 实装 jsonschema 4.26.0、attrs 26.1.0、jsonschema-specifications 2025.9.1、referencing 0.37.0、rpds-py 2026.9.1、typing_extensions 4.16.0；冻结清单见证据。执行器依然仅使用标准库。

## 命令与真实结果

openEuler 在上述干净源码检出中执行（下文 python3 实际使用 `~/projects/osdesign-venv/bin/python`）：

```bash
PYTHONPATH=src OSDESIGN_INTEGRATION=1 python3 -m unittest discover -s tests -v
python3 experiments/run_pipeline.py --output results/group-first
python3 experiments/run_pipeline.py --output results/group-healthy
python3 experiments/run_pipeline.py --output results/group-slow --passes 2
PYTHONPATH=src python3 work/validation/validate_evidence.py
```

目标系统最终 25 项测试全部通过（0 跳过）；包括 A 的故障/恢复测试和新增 8 项 B/C 测试。此前 2ac22b7 的 24 项也通过，后补损坏元数据回归用例。验证脚本是本次取证辅助文件，不是标准安装命令；归档中保留其源码。B/C 单测涵盖固定输入、手算负数聚合、SQLite 独立校验、错误输出、异常/未知状态、缺失正确性、不完整轮次、损坏元数据、历史门槛和 HTML 转义。

每轮参数：200 万行、请求 1000 组、种子 20261117、null/100/50 三档，每档一次预热与五次测量，60 秒超时，固定种子打乱执行顺序。输入 SHA256：`3d80ed09a28153313096dd54e48453f1e3795fdca054a1ac42f7852747a04bce`。三轮输入相同，输入生成与 SQLite 参考计算在负载计时区间之外。

三轮合计 **54 份最终记录均为 success、清理成功、干净 Git**，全部符合 run 1.1 schema，全部 stdout 通过 SQLite 独立正确性校验。**45 条非预热记录进入性能分析，9 条预热被排除**。每轮计划数/配额分布/order_index/实际最终数一致，没有未最终化 pending；报告重算时 issues 为空。输入与负载文件运行前后哈希一致。

openEuler 基线配置对照：

| 配额（单逻辑 CPU %） | 测量数 | wall 中位数 s | CPU 中位数 s |
|---|---:|---:|---:|
| null（未设本地配额） | 5 | 0.8158 | 0.7656 |
| 100 | 5 | 0.8158 | 0.7676 |
| 50 | 5 | 1.5175 | 0.7681 |

只描述本环境本次观察，不承诺精确倍增。父级/宿主机仍可施加约束。默认任务较短，启动、缓存、采样等待与宿主机抖动可能影响差异；不能据此得出生产性能结论。

## 历史复核规则检查

阈值/样本门槛在提交 `47a2316` 中先行固定：两边每档至少五条独立记录，耗时中位数比大于 1.15 才提示复核；没有根据后续验收数据调整。基线是 47a2316 的 WSL 首轮或 2ac22b7 的 openEuler 首轮；各环境仅与自身独立复测比较。

| 环境与样本 | null 耗时比 | 100% 耗时比 | 50% 耗时比 | 预设规则结果 |
|---|---:|---:|---:|---|
| openEuler 正常复测 | 0.9999 | 1.0001 | 0.9999 | 三档均 no_threshold_signal |
| openEuler 两遍处理变慢样本 | 1.9213 | 1.9215 | 2.0565 | 三档均 slowdown_needs_review |
| WSL 正常复测 | 0.9997 | 1.0001 | 1.0413 | 三档均 no_threshold_signal |
| WSL 两遍处理变慢样本 | 1.9030 | 1.9035 | 2.0296 | 三档均 slowdown_needs_review |

受控变慢增加完整数据处理遍数，仍返回相同正确结果，属于真实测量的验证变体，不伪造计时。当前有限样本中健康对照没有触发阈值、明显变慢均给出信号；**不能据此声称准确率/统计显著性、无退化或根因已确认**。小幅退化、临界阈值、广泛抖动与多机器表现未验收。

另对实际已读取数据的内存副本分别改变 input_id、schema_version、environment，并构造 complete=false：四种负向场景的每档均返回 unable_to_compare，原始文件未改动。辅助检查及完整兼容原因在 `negative-checks.json`。这属于规则拒绝检查，不能当作新的真实性能样本。

## 证据与复建

- [目标系统归档](../../evidence/integration/bc-openeuler-20261117.tar.gz)：三轮原始最终记录、stdout/stderr/启动/测量/清理、配置、正确性、输入元数据、参考结果、报告、测试日志、依赖/版本/时间和验证脚本。
- [WSL 归档](../../evidence/integration/bc-wsl-20261117.tar.gz)：独立保存三轮相应证据、测试与历史比较；原始首轮提交 47a2316、正常/变慢提交 804aeb6、最终报告重算提交 2ac22b7。WSL 全套 24 项测试在 8ff1f9b 通过，随后报告表格在 Windows 通过相关 7 项测试。
- 归档 SHA256 见 [清单](../../evidence/integration/SHA256SUMS)。不包含体积较大的 input.csv；用同版生成器、种子/规模可复建并核对上述哈希。未伪造不存在的原始输入文件。其余日志保留运行当时路径，不为搬迁改写。
- 本机展开结果在 `results/bc-openeuler-20261117/` 和 `results/bc-wsl-20261117/`，均 Git 忽略；唯一共享证据是上述归档。可解包后用源码中的 `python3 -m report` 从最终记录重算到新的 HTML 路径，不执行负载。

## 发现、修正与未完成事项

- openEuler 初次 SSH 因来宾旧网段与 Windows 默认交换机新网段不一致而不可达；用户重启后 DHCP 恢复，验证既有主机密钥后连接，并备份/更新本机 SSH 别名地址。没有改安全策略或主机资源配置。
- Windows 跨 Python 版本下载依赖时忽略了 Python<3.13 的 typing_extensions 条件；首次目标机离线安装失败，补齐包仓库提供的 wheel 后成功。没有把失败安装写成测试成功。
- HTML 已通过内容转义和报告数据检查，含每次耗时点图、历史表格及 run_id 追溯。浏览器工具拒绝 file 协议，未进行浏览器视觉验收，也未绕过限制。
- 所有执行均由同一代理完成：不等同非实现者独立复现，不替代三名成员理解/讲解和贡献确认。
- 仍待：非实现者复验、同类工具公平实测比较、统计误报/漏报扩展验收、最终视频/PPT、导师/报名/GitLab 与正式赛事提交。开发完成不代表这些事项完成。
- 本轮仅本地提交；未推送、未创建 PR、未合并共享分支、未正式提交比赛。
