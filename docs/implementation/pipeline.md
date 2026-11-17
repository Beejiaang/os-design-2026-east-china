# 聚合负载、分析与离线报告

日期：2026-11-17。按用户授权跨 A/B/C 推进，代码由代理实现，不表示三名成员已分别完成人工贡献或交叉验收。run 1.1 / config 1.0 未修改。

## 从源码运行

目标为 Python 3.11+、cgroup v2、systemd 用户管理器和 CPU 控制器。执行器仍只用标准库；分析依赖 jsonschema，先安装开发/报告依赖。在仓库根目录：

```bash
python3 -m pip install -e '.[report]'
export PYTHONPATH="$PWD/src"
python3 -m runner doctor
python3 experiments/run_pipeline.py --output results/group-first
```

目标 openEuler 的已有环境可用 `~/projects/osdesign-venv/bin/python` 替代 python3。输出路径必须不存在。默认 200 万行、1000 组、种子 20261117，三档 null/100/50，先每档预热一次，再各测量五次；顺序由种子打乱，超时 60 秒。这些是验证流程的初始参数，不是统计功效或代表性承诺。小试可加 `--rows 10000 --repeats 1 --warmups 0`。

产物：input.csv、input.json、reference.json、experiment/（A 的全部原始文件及 correctness.json）、summary.json、report.html。HTML 无外部资源，离线打开即可；原始记录路径及 SHA256 在报告中列出。不要只共享 HTML 后删除原始目录。

已存在的实验可离线重算，不再次执行负载：

```bash
PYTHONPATH=src python3 -m report results/group-first/experiment --output results/group-first/report-recomputed.html
PYTHONPATH=src python3 -m report results/group-current/experiment --baseline results/group-first/experiment --output results/group-current/history.html
```

CLI 退出 0 表示实验完整且有可用样本，不表示历史无退化。CLI 退出 1 表示不完整/无可用样本，2 表示输入/依赖等错误。pipeline 在样本数不足、任务失败或正确性不通过时返回非零；SIGINT/SIGTERM 保留 A 的中断状态。准备输入/SQLite 校验阶段未进入受限负载测量区间。

## B：输入、负载与正确性

`workloads/dataset.py` 用明确定义的 32 位 LCG 生成整数 CSV，逐行使用高位生成组号及 -10000…10000 的整数值。固定种子/规模下字节一致；LF 行尾跨系统稳定。输入标识使用生成器版本和完整输入 SHA256；input.json 保存种子、行数、请求组数和哈希。小输入不保证覆盖全部请求组。

`workloads/group_aggregate.py` 单进程逐行读取，以字典累计每组 count/sum，输出按组号排序的紧凑 JSON。输出只含数据，不含耗时、路径或其他非确定内容。计时包含读取固定 CSV、聚合及序列化；默认首次预热用于减轻缓存影响，不能证明所有缓存/宿主机干扰均已消除。输入上限 1000 万行，独立参考结果使用内存 SQLite，不能据此声称大规模生产可用。

正确性实现不调用聚合算法：SQLite 导入固定输入，再独立执行 GROUP BY、COUNT、SUM 和 ORDER BY。pipeline 在运行前算参考结果，在运行后逐个核对 stdout 的精确规范字节，同时检查输入/负载文件运行前后 SHA256 不变。correctness.json 将方法版本、input_id、workload_version 和每个 run_id/stdout 哈希绑定。它是本机派生验证证据，不是第三方签名或人工作业证明。错误输出即使退出 0 也排除。

## C：消费、汇总与比较

权威入口为每个 run_id/result.json，不信任派生 JSONL/CSV 覆盖原记录。分析使用 run 1.1 schema、拒绝 NaN/Infinity/重复 JSON 键，再核对目录/run_id、计划配额和预热分布、order_index、配置标识、完成状态及最终计数；检查缺失最终记录的 pending。非法记录和元数据问题在报告列出，不能称完整实验。

每条记录通过 A 的兼容前提自检（含 measured/success、非预热、配额与清理、有限指标、干净 Git、父级限制）后，再核对独立正确性证据与 stdout 文件哈希。失败、未知状态、模拟、恢复、预热和缺失证据均保留原因。历史 1.0 归档不迁移为 1.1；当前分析拒绝其结构版本。

配置对照固定输入、实现、环境与父级限制，允许配额不同；显示每档中位数、最小/最大值、CPU 时间及逐次 run_id。组内所有计划测量都通过才标可比；实验不完整不给可比倍数。null 是未设置本地配额，不代表没有父级/宿主机限制。耗时倍数是描述性观察。

历史比较逐条调用 `runner.compatibility.check_compatibility`，允许 workload_version 改变但要求输出、输入、同档资源、环境与执行器兼容。每边至少五个不同且互不重叠的已校验样本。规则预设为中位数耗时比大于 1.15 时 `slowdown_needs_review`，否则 `no_threshold_signal`；前提或样本不足为 `unable_to_compare`。这是探索性复核信号，15% 和五次均未经过独立误报/漏报验收，不是统计显著性检验，不宣称“无退化”、准确率或根因。

受控变慢样本可运行 `python3 experiments/run_pipeline.py --output results/group-slow --passes 2`。该参数令负载完整处理同一 CSV 两次，仅输出最后一次相同结果；版本标识包含文件哈希和 passes。它是明确设计的变慢校验变体，不能当作真实版本优化/退化事故，也不是故障注入伪造计时。与正常 `--passes 1` 的独立复测分别收集，用于检查既定复核规则的行为。

## 下一阶段验收

1. 目标 openEuler 的干净提交完整 pipeline 已由代理实测，所有测量和每次正确性结果见集成验证；后续由非实现者复验。
2. 已按预先固定规则收集互不重叠健康复测及输出一致的额外工作量版本；范围诊断/边界实验见扩展验证。后续扩大机器/抖动与阈值附近样本，不能凭有限场景估算普遍误报率。
3. 非实现者从指定提交重跑并解释单位/限制，再评估阶段通过；WSL 流程检查不能替代 openEuler 验收。
4. GNU time+systemd-run 正常场景实测已完成；其他完整框架评估、视频/PPT、导师/报名/GitLab 与正式提交仍按提交清单推进。

## 重复次数与预热设计依据

默认每档 n=5，采用中位数减少少数极端耗时对中心值的影响，同时控制三档及多版本重复执行的时间成本。五条是当前探索流程的最小约定，不是统计功效计算或充分样本量证明；中位数不能消除系统性偏差、时间漂移或低频干扰。应同时查看逐次点、min/max及阈值敏感性，波动较大时追加预先声明的独立重复。

[200万行既有基线](../validation/pipeline-validation.md)的 null 与100%档 wall 中位数均约0.8158s，CPU为0.7656/0.7676s；本批接近只说明该次环境观察，不能用近零差异反证 n=5 普遍足够。工具对照与更大输入另有计时边界，不混作同一基线。

每档一次预热意在减轻首次读取、代码启动和缓存状态差异；预热作为原始记录保留，明确排除测量样本。一次预热不保证缓存稳定或无宿主机影响。样本/阈值规则在正式验收前固定，不依据事后好看结果重新挑选样本；更多重复及独立机器验证仍待开展。

术语统一入口：[资源、计时与完成状态](../contracts/glossary.md)。
