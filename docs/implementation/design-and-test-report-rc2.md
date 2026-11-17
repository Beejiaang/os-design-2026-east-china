# 面向 openEuler 数据处理任务的 CPU 资源约束与性能回归分析工具

设计与测试报告　2026年11月17日　候选材料 RC2

本工具在固定Linux环境中执行单进程数据聚合任务，核验CPU配额、输出正确性与清理状态，再展示配置差异和兼容条件下的历史性能变化。当前源码已在openEuler通过37项测试及默认完整流程；三种规模和三类工具的实测数据可追溯到原始记录。历史比较仍是探索性复核规则，不提供统计准确率、生产可靠性或根因确认。

本版纳入RC1之后的hyperfine对照、阈值矩阵、规模与内存扫描、Linux负载采样、观察范围图和全src指纹。每批数据保留原测量提交，不把材料更新算成重新测量。RC1原文件、标签和哈希保留，RC2仅为新候选材料名称，尚未创建标签或正式发布。

| 对象 | 固定版本 | 核验范围 |
|---|---|---|
| 最新实测源码 | bb288cb | 37项0跳过、默认18次、规模扫描54次 |
| 本轮材料起点 | 7ef8f88 | 包含P0/P1/P2及历史交接，运行代码与bb288cb一致 |
| 三类工具测量 | d8a331e | 同批54次对照，45条测量、9条预热 |
| 规则矩阵来源 | 8d76aed / 25b7f32 | 48次原始记录及后续派生诊断，未改默认阈值 |
| 协议与指纹 | run1.1 / config1.0 | 指纹策略src-py-v2，旧记录不重写 |

验证由代理执行，不能替代非实现者复验。真实团队信息、导师、报名、正式视频及官方平台接收仍需落实；未用角色代号认领人工贡献。

<!-- pagebreak -->
## 任务范围与系统结构

适用场景是在cgroup v2和systemd用户服务可用的固定Linux环境中研究资源行为。输入为固定种子整数CSV；负载按组累计count和sum并输出排序JSON；SQLite用独立SQL聚合校验每份输出。首版不扩展成通用运维、自动调优、分布式数据库或生产诊断系统。

| 环节 | 主要路径 | 输出和责任 |
|---|---|---|
| 执行与采集 | src/runner、src/collector | 配额快照、指标、异常与清理证据 |
| 数据与校验 | workloads | 固定输入、聚合实现、SQLite参考 |
| 实验编排 | experiments | 默认流程、工具对照、规则和规模实验 |
| 分析与报告 | src/analysis、src/report | 样本排除、前提检查、分布与离线追溯 |

每次运行创建UUID命名的用户临时服务。CPUAccounting、CPUQuota、KillMode=control-group、停止期限与RuntimeMaxSec共同约束受控负载；worker在服务内采样，runner等待测量并核验清理，再保存最终result.json。只控制本工具创建的临时服务，不修改其他服务或全局安全设置。

100%是一个逻辑CPU的时间上限，50%不是整机CPU利用率，null仅表示本工具未主动设置本地配额；祖先与宿主机仍可能限制。不能以wall恰好翻倍作为配额通过标准，应读取实际cpu.max与父级控制信息。

SIGINT/SIGTERM停止后续调度并保留interrupted。失败、超时、缺指标、worker异常和cleanup_failed分别保存。执行器强制丢失后，recover只在同用户、机器及启动周期核验所有权与清理，恢复结果为aborted，不改为成功。该机制不是恶意代码沙箱、断电持久性或硬实时保证。

<!-- pagebreak -->
## 记录协议与比较前提

result.json是权威最终记录；JSONL/CSV是派生索引，pending/started/measurement不能替代最终成功记录。测量只纳入真实measured、success、非预热、配额及清理通过、干净可识别Git提交、功能校验与stdout哈希一致的记录；失败与排除理由不丢弃，不补造零值。

| 指标 | 单位 | 精确含义 |
|---|---|---|
| wall_seconds | 秒 | worker单调时钟区间，包含区间内快照、启动、等待及采样开销 |
| cpu_seconds | 秒 | 已回收子进程user加system，不含worker本身 |
| cpu_stat_delta | 微秒或计数 | 内核cgroup采样差值，包含worker区间开销，不能混作子进程CPU时间 |
| host-load.jsonl | 1/5/15分钟负载 | 执行Linux来宾的/proc/loadavg，不是物理宿主机CPU利用率 |

Linux负载在开始、结束和期间约每5秒记录，读取/写入失败明确保留。environment.json引用附加linux-load-v1证据，不将动态值放进每条记录的环境兼容指纹，也不进入阈值判定；采样自身仍有少量观测开销。

代码身份采用src-py-v2：递归覆盖src全部.py，按相对POSIX路径排序，将路径长度、路径、内容长度及内容分帧，加入算法域标记后计算SHA256。run1.1字段形状不变，旧legacy指纹不回写。报告/分析源码改变也会使指纹改变，是本任务接受的保守取舍；新旧摘要不同即拒绝直接比较，需在新源码重新建立基线。

历史比较先核对输入、同档资源、输出、环境、实际父级和代码指纹；允许负载版本变化。未知状态、混版、未完成实验和证据不足均拒绝比较，不将无法判断写成正常。精确字段以docs/contracts/data-contract.md与schemas为准。

<!-- pagebreak -->
## 测试与干净源码复验

目标openEuler24.03 LTS-SP4，x86_64，内核6.6.0-159.4.3.154.oe2403sp4，Python3.11.6，4vCPU，systemd255。执行器只用标准库；分析依赖jsonschema，开发extra另含Ruff0.17.5。实验未调整GPU功率、主机资源或安全策略。

| 固定源码及任务 | 全量测试 | 跳过数 | 默认流程 |
|---|---|---|---|
| f96e456 静态检查 | 29通过 | 0 | 18次，15测量 |
| 5e0a9d9 依赖复用 | 29通过 | 0 | 18次，15测量 |
| 1bde76a 负载采样 | 32通过 | 0 | 18次，15测量 |
| 2d60a88 观察范围图 | 34通过 | 0 | 18次，15测量 |
| 0be73a7 指纹策略 | 36通过 | 0 | 18次，15测量 |
| bb288cb 规模扫描 | 37通过 | 0 | 18次，15测量 |

六个提交逐个干净检出，分别运行全量测试、pip check、Ruff、默认pipeline和独立完整性/正确性证据检查；各轮结束时临时服务为零、工作树干净。默认流程共108次，各轮3条预热排除，不混作同一历史性能基线。新增8项单测覆盖采样异常、SVG几何/缺失数据、指纹分界和内存解析。

```bash
python3 -m pip install -e '.[dev]'
python3 -m pip check
python3 -m ruff check src workloads experiments tests scripts
PYTHONPATH=src OSDESIGN_INTEGRATION=1 python3 -m unittest discover -s tests -v
python3 experiments/run_pipeline.py --output results/new-run
```

Windows3.12的37项中28通过、9项系统测试按门控跳过，不记为目标机通过。CI配置为Ubuntu与Python3.11/3.12矩阵，但GitHub在线运行尚未发生。日志、安装清单和原始记录见evidence/improvement下两份P1归档及SHA256SUMS。

<!-- pagebreak -->
## 规模与内存峰值实测

固定50万、200万、800万行，每档1000组、种子20261117；各null/100/50配额一次预热、五次测量。预热先行，其后规模/配额混排。54次全部独立SQLite校验、配额与清理通过，输入/负载哈希前后不变，45条非预热进入下表。

| 行数及配额 | wall中位数秒 | CPU中位数秒 | RSS峰值中位数KiB |
|---|---|---|---|
| 50万 / null | 0.20 | 0.20 | 17364 |
| 50万 / 100% | 0.20 | 0.20 | 17372 |
| 50万 / 50% | 0.38 | 0.20 | 17408 |
| 200万 / null | 0.77 | 0.76 | 17404 |
| 200万 / 100% | 0.77 | 0.76 | 17408 |
| 200万 / 50% | 1.50 | 0.76 | 17404 |
| 800万 / null | 3.06 | 3.04 | 17404 |
| 800万 / 100% | 3.05 | 3.03 | 17396 |
| 800万 / 50% | 6.06 | 3.05 | 17404 |

每格n=5。GNU time1.10外层记录wall/user/system，分辨率0.01秒；内层-f %M记录聚合进程最大驻留集，Linux按KiB记录。wall/CPU包含内层timer启动和等待，与runner worker计时范围不同，不能直接按本表和旧runner耗时排速度。输入生成、SQLite参考和整机内存均不在该RSS口径内。

本机100%配额下wall中位数从0.20秒增至0.77、3.05秒；固定1000组时RSS峰值中位数约17MiB，五次最大峰值为17408至17416KiB量级。时间随行数近似按规模增长只是本环境观察，不证明普遍线性、生产规模上限、跨机器迁移或统计显著性。

每次保留argv、stdout、时间/内存原文、控制快照与清理结果。大CSV不入归档，固定生成参数、input.json哈希与参考结果保留，可复建核对。原始证据为evidence/improvement/p1-final-openeuler-20261117.tar.gz，测量源码bb288cb。

<!-- pagebreak -->
## 同类工具实测与计时边界

固定同一400万行CSV、Python聚合源码、输出和父级限制；本队、GNU time加systemd-run、hyperfine适配流程各三档、一次预热五测量，共54次全部正确性/配额/清理通过。测量源码d8a331e，45条正式测量、9条预热排除。

| 方法及配额 | 内部wall秒 | 内部CPU秒 | 外部命令秒 |
|---|---|---|---|
| 本队 / null | 1.5673 | 1.5346 | 1.6326 |
| 本队 / 100% | 1.5672 | 1.5347 | 1.6442 |
| 本队 / 50% | 3.0714 | 1.5380 | 3.1468 |
| GNU+systemd / null | 1.5200 | 1.5200 | 1.5671 |
| GNU+systemd / 100% | 1.5300 | 1.5200 | 1.5777 |
| GNU+systemd / 50% | 3.0400 | 1.5200 | 3.0875 |
| hyperfine适配 / null | 1.5400 | 1.5300 | 1.6096 |
| hyperfine适配 / 100% | 1.5300 | 1.5200 | 1.6072 |
| hyperfine适配 / 50% | 3.0600 | 1.5300 | 3.1288 |

GNU time1.10提供单命令计时，systemd255提供服务与资源控制；hyperfine1.19.0提供预热、重复和外部命令JSON计时。逐次输出留存、SQLite参考、三档实际控制与清理核验由本队脚本补充，不能认领为第三方原生能力或本队发明底层CPU隔离。

hyperfine以--shell=none、--warmup 1、--runs 5调用适配器，其外部times包含Python导入、服务创建、快照、GNU time、退出与清理；其内部wall/CPU仍来自GNU time。前36次本队/原生命令混排，hyperfine随后按100/50/null分批执行，有时间顺序混杂。计时边界和打印精度不同，不输出工具速度排名。

工具均在普通用户目录准备，未全局安装；来源URL、压缩包/二进制SHA256与版本日志留存，未独立验证上游签名。未测的异常/权限场景或lkp-tests、mugen等框架不能被写成不支持。证据见evidence/comparison/improve01-openeuler-20261117.tar.gz。

<!-- pagebreak -->
## 探索性阈值与检出矩阵

默认每边至少五条不同且互不重叠的合格记录，中位数wall比严格大于1.15才提示slowdown_needs_review；否则为no_threshold_signal，证据不足为unable_to_compare。五次与单次预热兼顾重复成本和首次缓存影响，不是统计功效证明；中位数也不能排除漂移或系统性干扰。

下表使用既有48次固定100%配额实验。行是额外工作量，不是实测wall增长承诺；每格为7条基线对7条当前记录，6条场景预热排除。此为事后阈值敏感性分析，默认15%未调参。两次健康对照分别保留，不合并共享基线。

| 额外工作量场景 | 阈值10% | 阈值15% | 阈值25% |
|---|---|---|---|
| 0% 健康复测1 | 未触发 | 未触发 | 未触发 |
| 0% 健康复测2 | 未触发 | 未触发 | 未触发 |
| 5% | 未触发 | 未触发 | 未触发 |
| 15% | 需复核 | 需复核 | 未触发 |
| 25% | 需复核 | 需复核 | 需复核 |

15%变体实测比约1.1598，25%变体约1.2557，因此越过对应阈值；不能由工作量参数直接推断耗时。逐格run_id、比值和原归档哈希见evidence/comparison/threshold-matrix-20261117.json。有效前提均成立，故表中无unable_to_compare；不完整、少样本、重叠run_id、输入/环境不匹配的拒绝分支另有派生检查，不增加真实运行数。

观察范围由当前最小/基线最大至当前最大/基线最小构成。真实健康场景约0.9997至1.0320，边界场景约1.1594至1.1599；本批均未跨1.15。报告以区间与参考线展示敏感性，但这不是置信区间，未跨阈值也不证明统计稳定。跨阈值分支由明确测试夹具验证，未伪造真实样本。

有限场景不是普遍误报/漏报率、统计显著性或独立准确率验收。没有触发阈值不能写成无退化，性能变化也不能直接写成根因确认。

<!-- pagebreak -->
## 贡献来源与使用边界

本队增量是将受限执行、异常与清理证据、版本化最终记录、固定输入、独立正确性、保守兼容门槛和离线追溯连接成可复验流程；成熟工具加脚本也可构建类似工作流。CPU控制、计时、SQL聚合和schema校验来自现有系统与库，不宣称底层机制原创。

| 能力 | 来源 | 本项目增量 |
|---|---|---|
| 服务与CPU时间上限 | Linux cgroup v2、systemd | 实际控制与父级核验、生命周期清理 |
| 功能参考结果 | SQLite | 输入/输出身份绑定与逐次校验 |
| 计时与内存 | GNU time、hyperfine | 同场景编排、逐次留证、边界披露 |
| 结构与报告 | jsonschema、Python | 最终记录优先、拒绝理由及离线追溯 |

原创代码MIT，原创文档CC BY-SA 4.0，第三方保留原许可。源码仓库不含GNU或hyperfine二进制；若分发离线wheels，应保留包内许可与元数据。团队真实姓名、贡献与工时不从代理生成记录推定。

教学材料提供三档配额与受控变慢实验、预期观察、思考题和报告模板。可帮助记录现象，但未评估真实学生学习效果。代理自动测试、干净检出或版式检查不等于非实现者复现；至少仍需真实操作者按README复验并记录问题。

本轮未覆盖其他机器、冷缓存、温度频率、全面宿主机干扰、生产数据和普遍统计准确率；loadavg是来宾证据，不能排除不可见物理宿主机影响。当前源码运行与材料整理不替代报名、导师、视频或平台接收。

<!-- pagebreak -->
## 复现与证据索引

从支持systemd用户服务和cgroup v2的Linux干净源码检出开始，Python3.11以上。输出目录必须不存在，保留完整原始目录；报告HTML不能代替原始记录。正式基线需固定源码、输入、资源与环境，不能将不同机器或不同指纹样本混合。

```bash
python3 -m pip install -e '.[report]'
PYTHONPATH=src python3 -m runner doctor
python3 experiments/run_pipeline.py --output results/first
PYTHONPATH=src python3 -m report results/first/experiment --output results/recomputed.html
```

| 验证内容 | 仓库记录 | 原始证据位置 |
|---|---|---|
| 最新37项与规模 | P1验证记录 | evidence/improvement/p1-final-openeuler-20261117.tar.gz |
| 分提交全量复验 | 同上 | evidence/improvement/p1-staged-openeuler-20261117.tar.gz |
| 三类工具54次 | 对照验证记录 | evidence/comparison/improve01-openeuler-20261117.tar.gz |
| 阈值矩阵 | 同上 | evidence/comparison/threshold-matrix-20261117.json |
| 初轮与规则原始记录 | 初轮验证记录 | evidence/integration、evidence/comparison |

每个evidence目录的SHA256SUMS核对原始归档；docs/validation/material-versions.md与材料manifest核对交付字节。本文表格四舍五入显示，原始JSON保留完整精度。源文件和原始测量版本分别注明，不将后续材料提交冒充新测量。

技术机制来源包括Linux cgroup v2内核文档、目标systemd255说明、GNU time1.10手册和hyperfine1.19.0发布说明，确切链接和哈希在docs/records/sources.md与同类工具记录。赛事依据保留原技术方案和docs/project/submission-checklist.md，截止与账号内字段须按官方最新通知核验。

正式提交仍需团队确认人员/导师、报名与官方GitLab地址，补充真实非实现者验收和视频，保存接收时间、版本及凭据。当前候选材料和本地提交均不等于赛事接收，也未授权推送、PR、合并或新标签。
