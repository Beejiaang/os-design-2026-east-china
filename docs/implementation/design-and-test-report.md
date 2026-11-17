# 面向 openEuler 数据处理任务的 CPU 资源约束与性能回归分析工具

设计与测试报告　2026年11月17日　候选交付版 RC1

本文供团队复验与赛事技术评审阅读，汇总已实现的系统机制、功能与性能测试、同类工具比较、贡献和限制。固定输入分组聚合已接通资源约束、独立正确性校验和离线报告；openEuler 的代理实测支持这些具体流程可运行。当前历史比较提供探索性复核信号，尚不支持统计准确率、生产可靠性或根因结论。人工验收与视频演示按本轮用户要求留待后续。

本报告由代理根据仓库实现与原始记录整理，未替三名成员认领人工贡献。队名、姓名、指导教师、报名审核及正式 GitLab 尚无已确认记录，正式提交前须补充。完整工程以 Git 历史为准，本文不覆盖版本化协议或原始数据。

## 版本与证据对应关系

| 对象 | 实际版本 | 说明 |
|---|---|---|
| 当前运行代码 | 2697479 所含实现 | RC1 整理不改 runner、负载或分析逻辑 |
| 首轮 openEuler 测量 | 2ac22b7 | 1028dd8 修正分析后重算，未改原记录 |
| 扩展比较测量 | 8d76aed | 25b7f32 增补范围诊断，判定规则不变 |
| 新环境安装验证 | 57c865e | 全新检出和 venv，29项测试与三档小试 |
| 答辩 PPT | 20261117 v1 | 十页原生图表及备注，已在 PowerPoint 逐页检查 |
| 数据协议 | run 1.1 / config 1.0 | 历史 run 1.0 证据保留，不静默迁移 |

候选交付包附文件哈希和源码提交，固定原始归档的来源版本。材料版本允许不同，但必须明确对应关系；不能把较早测量说成最终文档提交上的新测量。

<!-- pagebreak -->
## 需求与系统结构

目标用户是在 Linux 固定环境下研究数据任务资源行为的学生和开发者。首版回答三个问题：CPU 时间上限是否实际设置，任务是否返回正确结果，兼容条件下的耗时变化是否需要复核。范围为单进程整数分组聚合、三档本地 CPU 配额、重复实验、异常证据和离线报告。

数据依次经过固定种子 CSV、受限服务中的字典聚合、SQLite 独立参考校验、最终记录核验、配置对照和历史比较。输入生成与参考计算在负载计时区间之外。编排脚本只调用各模块，不复制执行器的状态机。

| 模块 | 主要路径 | 交付内容 |
|---|---|---|
| 执行与采集 | src/runner、src/collector | 服务控制、测量、异常、清理与最终记录 |
| 输入与校验 | workloads | 确定性 CSV、整数聚合、SQLite 参考结果 |
| 实验编排 | experiments | 三档流程、原生工具对照、受控变慢实验 |
| 分析与展示 | src/analysis、src/report | 严格消费、样本排除、比较及离线 HTML |

每次运行创建唯一 UUID 的 systemd 用户临时服务，启用 CPUAccounting，按配置设置 CPUQuota，并使用 control-group 终止范围和运行看门狗。worker 读取 cgroup v2 实际控制值后启动负载；runner 在结束后清理服务，核验卸载及进程组为空或删除，才写 result.json。100% 是一个逻辑 CPU 的时间上限；null 表示未设本地配额，父级和宿主机约束仍可能存在。

SIGINT 与 SIGTERM 会停止后续调度并保留 interrupted。失败、超时、worker 崩溃、指标缺失及清理失败分别记录。supervisor 被硬终止后的恢复只在同用户、同机器、同启动周期内核验，最终为 aborted，不能恢复成成功性能样本。该流程不提供恶意代码沙箱、断电持久性或硬实时保证。

<!-- pagebreak -->
## 数据协议与分析规则

result.json 是单次权威最终记录，JSONL 和 CSV 是派生索引。pending、started、measurement 均不能替代成功记录。wall_seconds 来自 worker 的单调时钟区间，包含区间内快照保存、文件打开、进程启动、等待回收与末次采样；cpu_seconds 是已回收子进程 user 加 system 秒；cgroup 统计是采样差值，含 worker 区间开销。三者口径不同。

输入为 group,value 整数 CSV，包含负值。固定 LCG 生成器、种子、规模和 LF 行尾确定输入字节；input_id 绑定生成器与输入哈希。负载按组累计 count 和 sum，排序输出紧凑 JSON，workload_version 绑定源码哈希与实际工作量参数。SQLite 导入同一输入并独立执行 GROUP BY、COUNT、SUM、ORDER BY，不调用负载字典函数。每次校验绑定 run_id 和 stdout 哈希，并核对运行前后输入与负载哈希。

分析先验证 schema、目录与 run_id、计划数、各档预热及测量数、执行顺序和完整状态。未知版本与状态、非有限数、JSON 重复键、缺失最终记录、非法元数据均显式报告。synthetic、失败、预热、脏 Git、资源或清理证据不足、指标缺失、正确性失败及 stdout 哈希不符均排除，不填补为零或正常。

配置对照固定输入、实现、环境及父级限制，允许本地配额不同。历史比较允许实现版本改变，但要求输入、功能输出、同档资源、环境和执行器兼容；每边至少五条不同且互不重叠的合格样本。中位数比大于 1.15 才返回 slowdown_needs_review，否则返回 no_threshold_signal；证据不足返回 unable_to_compare。阈值先于验收实验固定，未按后来的结果调参。

报告给出各次耗时、min/max、中位数、排除原因、run_id、原始文件路径及 SHA256。范围诊断取当前最小值除基线最大值至当前最大值除基线最小值，观察其是否跨过 1.15。此范围不是置信区间，未跨阈值也不能证明统计稳定。退出成功、功能正确、配额生效、性能变化与根因确认是不同层次的结论。

<!-- pagebreak -->
## 功能与完整流程验证

目标环境为 openEuler 24.03 LTS SP4、x86_64、内核 6.6.0-159.4.3.154.oe2403sp4、Python 3.11.6、4 vCPU、systemd 255。执行器仅用标准库；报告环境使用 jsonschema 4.26.0 及归档中的冻结依赖。未改 GPU 功率、主机资源或安全策略。

最终扩展源码在目标机通过29项测试，0跳过，覆盖确定性输入与手算负数聚合、SQLite 校验、错误输出、损坏元数据、未知状态、缺失正确性、不完整轮次、历史门槛、HTML 转义、GNU 时间解析及系统异常与恢复。故障注入记录单列，不能计入性能测量。

首轮每次使用200万行、请求1000组、种子20261117，每档一次预热和五次测量，三档顺序按固定种子打乱，超时60秒。基线、正常复测和两遍处理各18次，总54份最终记录均 success、配额与清理核验通过、输出通过独立参考校验；45条非预热参与性能分析，9条预热排除。

| openEuler 基线配额 | 合格测量数 | wall 中位数秒 | CPU 中位数秒 |
|---|---:|---:|---:|
| null | 5 | 0.8158 | 0.7656 |
| 100% | 5 | 0.8158 | 0.7676 |
| 50% | 5 | 1.5175 | 0.7681 |

正常复测三档中位数比分别为0.9999、1.0001、0.9999，均未触发信号。两遍处理输出不变，耗时比分别为1.9213、1.9215、2.0565，均提示复核。这是受控增加工作量的真实执行，不能当作真实生产版本事故。Ubuntu WSL 另存54次记录，基线不与 openEuler 混合。

证据在 evidence/member-a、evidence/integration 和对应 SHA256SUMS。大 CSV 不在性能归档中，可按种子与规模复建并核对输入哈希；原始绝对路径保留运行时值。新源码检出及全新 venv 又完成离线可编辑安装、29项测试与三档小试，pip check 和 CLI 通过；同一代理与虚拟机不等于非实现者或第二台机器复现。

<!-- pagebreak -->
## 原生工具对照与规则边界

比较对象是 GNU time 1.10 加 systemd-run 255。GNU 源码来自官方 HTTPS，普通用户目录未修改编译，无全局安装；下载哈希与日志在证据中，未验证上游签名。两套流程共享400万行输入、Python、负载、父级限制与输出，方法和配额按固定种子混排。各工具每档一次预热、五次测量，共36次，30条非预热用于描述性对照。

| 流程 | 配额 | wall 中位数秒 | CPU 中位数秒 |
|---|---|---:|---:|
| 本队 | null | 1.5673 | 1.5360 |
| GNU time 加 systemd-run | null | 1.5300 | 1.5300 |
| 本队 | 100% | 1.5673 | 1.5451 |
| GNU time 加 systemd-run | 100% | 1.5400 | 1.5300 |
| 本队 | 50% | 3.1206 | 1.5451 |
| GNU time 加 systemd-run | 50% | 3.0400 | 1.5300 |

GNU 与本队的计时边界、打印精度不同，表格不能用来排名速度。循环、独立校验、实际控制快照和清理核验由本队比较脚本补充，不能算成 GNU 自带功能。底层 CPUQuota 与进程控制均由 systemd 和 cgroup 提供。

规则实验固定100%配额，预先写入基线、正常1、额外5%、额外15%、额外25%、正常2六场景。每场景一次预热、七次测量，总48次，42条非预热进入比较。五个当前场景相对基线中位数比依次为1.0000、1.0640、1.1598、1.2557、0.9999；其中15%和25%变体提示复核，其余无阈值信号。额外处理输入前缀并丢弃额外结果，完整输出仍正确。

五类派生负向前提均拒绝比较：四条样本、run_id 重叠、不完整、input_id 改变和环境改变。当前真实观测范围均未跨阈值；敏感分支由明确的单测夹具验证。场景顺序固定，未排除时间混杂；小于阈值的工作量增加不会保证报警。以上84次执行的原始数据在 evidence/comparison，不能推算普遍误报率、统计功效或根因。

<!-- pagebreak -->
## 安装复现与交付边界

运行前提为 Python 3.11以上、cgroup v2、可用 systemd 用户管理器及 CPU 控制器。以下命令从源码根目录运行，输出目录必须不存在。完整步骤、离线依赖限制与异常解释见 README 和 docs/validation/peer-reproduction.md。

```bash
python3 -m pip install -e '.[report]'
export PYTHONPATH="$PWD/src"
python3 -m runner doctor
OSDESIGN_INTEGRATION=1 python3 -m unittest discover -s tests -v
python3 experiments/run_pipeline.py --output results/reproduction
python3 -m report results/reproduction/experiment --output results/recomputed.html
```

完整流程生成 input.csv、输入元数据、独立参考、experiment 原始记录、correctness.json、summary.json 和离线 report.html。不要只留下 HTML 而删除原始目录。复验包附固定源码 Git bundle、Linux x86_64 CPython 3.11 的 wheels、证据与清单；其他系统或 Python 版本不能直接沿用这些二进制依赖。独立 wheel 分发尚未验收，支持源码与可编辑安装。

本队可举证增量是生命周期与异常证据管理、版本化最终记录、独立正确性绑定、保守兼容门槛、拒绝原因、离线追溯和固定场景复验流程。计时、CPU 隔离、SQLite 与 JSON schema 校验由既有系统或库提供，成熟工具加脚本也可形成类似工作流。未测试的 hyperfine、lkp-tests、mugen 与调优框架不能被写成“不支持”，也不能据此宣称本项目普遍优于它们。

原创代码 MIT，原创文档 CC BY SA 4.0；第三方组件保留原许可。没有将 GNU 源码或二进制纳入仓库。依赖分发附自带许可文件和 wheel 元数据，实际安装版本见原始冻结清单；封面概念图生成来源在 demo/assets/README.md，不是硬件照片或实测截图。

已完成代理自动检查与 PowerPoint 原生逐页版式检查；HTML 内容、转义和追溯已检查，浏览器 file 协议自动审批被拒绝，未绕过限制，视觉状态仍待核验。人工交叉验收与视频本轮排除。其他机器泛化、规模上界、峰值内存、冷缓存、宿主机温度频率、统计准确率均不在已验收范围。

<!-- pagebreak -->
## 来源与正式提交准备

技术证据以原始归档、各自 SHA256SUMS 及以下仓库记录为准。本文数值来自同一批既有记录，未追加虚构样本，未改写早期来源提交。引用资料说明机制，实际行为由固定目标机与工具版本的执行记录限定。

1. docs/contracts/data-contract.md 与 schemas：字段、单位、状态和恢复边界。
2. docs/validation/member-a-validation.md：17项系统测试、12次正常实验及单列故障记录。
3. docs/validation/pipeline-validation.md：两环境分别54次完整流程、配置和历史对照。
4. docs/validation/comparison-validation.md 与 docs/implementation/tool-comparison.md：36次工具对照、48次规则扩展及贡献边界。
5. docs/validation/reproduction-validation.md：全新检出和 venv 的安装检查；不替代人工验收。
6. docs/records/ai-usage.md 与 sources.md：代理参与、来源与限制。

一手机制资料包括 Linux cgroup v2 文档 https://docs.kernel.org/admin-guide/cgroup-v2.html ，GNU time 官方计时说明 https://www.gnu.org/software/time/manual/html_node/Time-Resources.html ，systemd 255 说明 https://www.freedesktop.org/software/systemd/man/255/systemd-run.html 。GNU 官方下载地址及源码内容哈希另见工具对照记录。

2026年11月17日重新查到 OS 应用开发赛道实际页面：https://course.educg.net/pages/contest/contest.jsp?contestCID=0&contestID=fLzatL8sv4E&doVisit=true&my=false 。页面显示应用开发阶段截至12月24日23时59分；通用结束字段02月01日不能作为作品延期依据。正式报名审核、提交字段与接收状态只能在实际账号中核验。

工程、设计与测试、过程资料和演示视频链接为原技术方案列出的交付类别；正式托管要求 GitLab，GitHub 协作不能代替比赛提交。原始赛事 PDF 不进入公开仓库。最终提交前须核实官方最新通知、填写真实团队与导师信息、提供官方 GitLab 项目、保存提交接收凭据。未取得这些事实前保持待办，不能将候选交付包写成已完成参赛提交。

