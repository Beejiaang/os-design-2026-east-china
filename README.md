# 2026 操作系统设计赛 · 华东区域赛

> 当前冻结：RC1 `086aff7` / `feat/a-release-preparation`；本轮开发在 `improve/*`，尚未重新冻结。
> 最近目标机验证：2026-11-17，源码 `a4f4c04`，29项测试0跳过，默认完整流程1轮18次；另有d8a331e同类复验。
> 当前硬缺口：[提交清单](docs/project/submission-checklist.md)中的人员交叉验收、视频、团队/导师与官方GitLab/平台接收；[本轮限制](docs/validation/improvement-progress.md)。

2026 年操作系统设计赛华东区域赛参赛项目仓库，涵盖选题分析、技术方案、源代码、测试实验、开发文档与演示材料。

三人团队已选择 **OS 应用开发赛道（赛道 2）的方向 A**，当前执行范围为 **面向 openEuler 数据处理任务的 CPU 资源约束与性能回归分析工具**。执行采集、固定输入分组聚合、独立正确性校验和离线报告已接通；在 openEuler 与 Ubuntu WSL 分别完成代理实测。非实现者验收仍需完成。

## 运行完整数据任务

在支持 cgroup v2 / systemd 用户服务的 Linux 中，从源码仓库根目录运行：

```bash
python3 -m pip install -e '.[report]'
python3 experiments/run_pipeline.py --output results/group-first
```

一条命令生成固定种子 CSV，执行三档配额、每档一次预热及五次测量，使用独立 SQLite 聚合校验输出，生成原始结果、summary.json 和离线 report.html。输出目录必须不存在；详细安装、离线重算、历史比较及测量边界见 [完整流程说明](docs/implementation/pipeline.md)，实测和限制见 [集成验证](docs/validation/pipeline-validation.md)。

历史比较仅输出探索性阈值信号及无法比较原因；未验收统计准确率，不把 `no_threshold_signal` 解释为“无退化”。已知变慢变体可加 `--passes 2`，结果保持一致，工作量明确增加。

## 实测对照与规则边界

已在 openEuler 完成本队与 GNU time + systemd-run 的 36 次正常任务对照，以及健康复测/额外 5%、15%、25% 工作量的 48 次规则实验。最终 29 项目标机测试全部通过；每份输出均独立校验，预热单列排除。方法、量化表和底层工具贡献见 [同类工具实测说明](docs/implementation/tool-comparison.md)，版本与原始证据见 [扩展验证](docs/validation/comparison-validation.md)。

新增“阈值敏感”展示只描述已观察范围是否跨阈值，不改变原 15% 中位数规则，不是置信区间。本队与原生命令的计时范围/精度不同，不能按耗时表给工具排速度名次。代码和材料已推送集成分支，PR/合并的实际状态见交接。

## 运行成员 A 的核心

在支持 cgroup v2 和 systemd 用户服务的 Linux 中，从项目根目录执行：

```bash
export PYTHONPATH="$PWD/src"
python3 -m runner doctor
python3 -m runner run examples/cpu.json --output results/cpu-first
OSDESIGN_INTEGRATION=1 python3 -m unittest discover -s tests -v
```

要求 Python 3.11+。输出目录必须尚不存在。包含三档 CPU 配额、预热与重复、原始 JSON/CSV、失败和超时处理、子进程清理核验、历史比较前提接口。完整说明及 B/C 接口见 [成员 A 交付](docs/implementation/member-a.md)，真实结果见 [验收记录](docs/validation/member-a-validation.md)。

当前输出协议为 run 1.1，含中断与恢复状态；可用 [真实样例](examples/measured-run-1.1.json) 接通解析。2026-11-16 的 A 干净源码在 openEuler 通过 17 项测试及 12 次正常实验；另保留 5 份故障注入最终记录，均单独列出并排除性能样本。恢复命令和机器格式见 [数据协议](docs/contracts/data-contract.md)。新增 B/C 验证不能直接继承这份目标系统结论。

## 候选交付 RC1

正式技术稿：[设计与测试报告](docs/implementation/design-and-test-report.md)、[可编辑 Word](demo/delivery/设计与测试报告_RC1.docx)、[PDF](demo/delivery/设计与测试报告_RC1.pdf)。十页 PPT 已完成原生 PowerPoint 逐页版式检查。版本、哈希与本轮实际检查见[候选验证](docs/validation/release-validation.md)，官方入口与所缺账号事实见[平台准备](docs/project/platform-readiness.md)。人工验收和视频演示按本轮要求留待后续；不能据此视为已提交参赛。

## 从这里开始

[评审导读：三份必读材料与分类索引](docs/reviewers-guide.md)；[Tasklist P0 改进进度与验证](docs/validation/improvement-progress.md)

演示与人员复验：[答辩工作稿](demo/presentation/答辩初稿_20261117_v1.pptx)、[讲解与20问](demo/defense-notes.md)、[非实现者复验指南](docs/validation/peer-reproduction.md)、[复验交付包](demo/delivery/README.md)。本轮另在新源码检出和全新 venv 验证可编辑安装、29 项测试及三档小试，记录见 [安装复验](docs/validation/reproduction-validation.md)。这些代理操作仍不能代替人员交叉验收。

目录入口：[文档分区导航](docs/README.md)、[工程文件存放规则](docs/project/directory-layout.md)。代码、负载、实验、协议、证据和演示材料分别放在对应目录；占位说明不代表 B/C 功能已完成。

使用 Agent 开发的队友先读 **[AGENTS.md](AGENTS.md)**，再看 **[统一口径](docs/project/project-contract.md)**、**[数据协议](docs/contracts/data-contract.md)** 和 **[角色交接/可复制启动任务](docs/handoff/agent-handoff.md)**。A 原集成分支是 `feat/member-a-runner`，首轮全链路为 `feat/bc-end-to-end`，对照/诊断为 `feat/b-comparison-validation`，旧材料/交接保留在 `feat/c-defense-reproduction`，当前候选集成分支为 `feat/a-release-preparation`；推送/PR/合并状态见交接，不默认远端已包含它。

1. 阅读 **[三人分工与阶段验收说明](docs/project/work-allocation.md)**：A 系统与集成、B 负载与实验、C 分析与报告，含课程关联、接口和验收条件。
2. 使用 **[提交清单](docs/project/submission-checklist.md)** 检查工程、文档、测试、视频、来源许可和官方平台提交；勾选须附证据。
3. 在 [讨论 Issue](https://github.com/Beejiaang/os-design-2026-east-china/issues/1) 保留问题与依据，按 [协作说明](CONTRIBUTING.md) 提交修改；姓名、实际投入与完成状态由团队补充。
4. 历史资料：[开发时间线](docs/history/timeline.md)、[10 月版学习与计划](docs/history/project-plan.md)、[八类选题分析](docs/history/topic-analysis.md)、[队员评价模板](docs/history/team-review.md)。EulerLens 是历史 B 方向候选。

**当前内部节点（2026-11-15 重排）：**11/22 完成环境与手动实验，11/29 完成可演示初稿，12/06 核心功能冻结，12/13 实验与主要材料齐全，12/20 完成正式提交核验。按已发章程的 **12/24 作品截止**倒排，后续以官方通知为准。

首版包括：一个结果可校验的分组聚合任务、三档 CPU 配额、自动重复运行、原始结果、失败与超时处理、配置对比报告；之后补齐兼容条件下的历史基线比较。先使用计算负载验证配额，再接入数据任务。建议周投入 A 10—12 小时、B/C 各 8—10 小时，含学习、开发与验证，实际承诺待填。

## 仓库定位

- 本 GitHub 仓库是团队持续协作的主仓库，用于分享、讨论，以及后续源代码、测试、开发文档与演示材料的版本管理。
- 赛事正式提交与开发过程留痕按组委会 GitLab 要求执行；选题后尽早建立比赛仓库并同步，不能以本 GitHub 仓库代替正式提交。
- 当前已有完整数据任务、独立校验和离线报告，openEuler 全链路代理实测通过；统计准确率与非实现者验收仍待完成，没有已验证的业务性能提升或诊断准确率。
- 本仓库不存放报名证件、个人联系方式、令牌、虚拟机镜像或用户提供的原始赛事 PDF。

## 资料结构

| 文件 | 用途 |
|---|---|
| [docs/project/work-allocation.md](docs/project/work-allocation.md) | 当前分工、范围、阶段验收与课程关联 |
| [docs/project/submission-checklist.md](docs/project/submission-checklist.md) | 正式材料、质量核验与提交记录 |
| [docs/history/project-plan.md](docs/history/project-plan.md) | 历史计划及专项学习资料，执行日期见新分工表 |
| [docs/history/topic-analysis.md](docs/history/topic-analysis.md) | 历史选题比较与综合评价 |
| [docs/history/team-review.md](docs/history/team-review.md) | 三人独立评价、试做记录与决策表 |
| [docs/records/sources.md](docs/records/sources.md) | 规则与技术资料来源、已知限制 |
| [docs/records/ai-usage.md](docs/records/ai-usage.md) | AI 辅助工作记录及后续填写模板 |
| [CONTRIBUTING.md](CONTRIBUTING.md) | 讨论、分支、PR 与证据记录方式 |
| [.github/ISSUE_TEMPLATE](.github/ISSUE_TEMPLATE) | 候选题讨论、验证任务模板 |

## 许可

本仓库原创文档采用 [CC BY-SA 4.0](LICENSE)，程序代码采用 [MIT](LICENSE-CODE)。第三方资料及引用内容保留原许可。

最近更新：**2026-11-17（Asia/Shanghai）**。赛事动态以官方平台最新公告为准。
