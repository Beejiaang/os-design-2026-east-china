# 2026 操作系统设计赛 · 华东区域赛

2026 年操作系统设计赛华东区域赛参赛项目仓库，涵盖选题分析、技术方案、源代码、测试实验、开发文档与演示材料。

三人团队已选择 **OS 应用开发赛道（赛道 2）的方向 A**，当前执行范围为 **面向 openEuler 数据处理任务的 CPU 资源约束与性能回归分析工具**。成员 A 的执行与采集核心已实现，并在 openEuler 验证；数据聚合负载、统计分析与完整报告待 B/C 接入。

## 运行成员 A 的核心

在支持 cgroup v2 和 systemd 用户服务的 Linux 中，从项目根目录执行：

```bash
export PYTHONPATH="$PWD/src"
python3 -m runner doctor
python3 -m runner run examples/cpu.json --output results/cpu-first
OSDESIGN_INTEGRATION=1 python3 -m unittest discover -s tests -v
```

要求 Python 3.11+。输出目录必须尚不存在。包含三档 CPU 配额、预热与重复、原始 JSON/CSV、失败和超时处理、子进程清理核验、历史比较前提接口。完整说明及 B/C 接口见 [成员 A 交付](docs/member-a.md)，真实结果见 [验收记录](docs/member-a-validation.md)。

## 从这里开始

使用 Agent 开发的队友先读 **[AGENTS.md](AGENTS.md)**，再看 **[统一口径](docs/project-contract.md)**、**[数据协议](docs/data-contract.md)** 和 **[角色交接/可复制启动任务](docs/agent-handoff.md)**。当前 A 集成分支是 `feat/member-a-runner`，未合并前请以该分支为依赖，避免直接从尚无实现的旧 main 开始。

1. 阅读 **[三人分工与阶段验收说明](docs/work-allocation.md)**：A 系统与集成、B 负载与实验、C 分析与报告，含课程关联、接口和验收条件。
2. 使用 **[提交清单](docs/submission-checklist.md)** 检查工程、文档、测试、视频、来源许可和官方平台提交；勾选须附证据。
3. 在 [讨论 Issue](https://github.com/Beejiaang/os-design-2026-east-china/issues/1) 保留问题与依据，按 [协作说明](CONTRIBUTING.md) 提交修改；姓名、实际投入与完成状态由团队补充。
4. 历史资料：[10 月版学习与计划](docs/project-plan.md)、[八类选题分析](docs/topic-analysis.md)、[队员评价模板](docs/team-review.md)。EulerLens 是历史 B 方向候选。

**当前内部节点（2026-11-15 重排）：**11/22 完成环境与手动实验，11/29 完成可演示初稿，12/06 核心功能冻结，12/13 实验与主要材料齐全，12/20 完成正式提交核验。按已发章程的 **12/24 作品截止**倒排，后续以官方通知为准。

首版包括：一个结果可校验的分组聚合任务、三档 CPU 配额、自动重复运行、原始结果、失败与超时处理、配置对比报告；之后补齐兼容条件下的历史基线比较。先使用计算负载验证配额，再接入数据任务。建议周投入 A 10—12 小时、B/C 各 8—10 小时，含学习、开发与验证，实际承诺待填。

## 仓库定位

- 本 GitHub 仓库是团队持续协作的主仓库，用于分享、讨论，以及后续源代码、测试、开发文档与演示材料的版本管理。
- 赛事正式提交与开发过程留痕按组委会 GitLab 要求执行；选题后尽早建立比赛仓库并同步，不能以本 GitHub 仓库代替正式提交。
- 当前已有执行与采集原型及真实实验；完整数据任务、统计回归检测与离线报告仍待接入，没有已验证的性能提升或诊断准确率。
- 本仓库不存放报名证件、个人联系方式、令牌、虚拟机镜像或用户提供的原始赛事 PDF。

## 资料结构

| 文件 | 用途 |
|---|---|
| [docs/work-allocation.md](docs/work-allocation.md) | 当前分工、范围、阶段验收与课程关联 |
| [docs/submission-checklist.md](docs/submission-checklist.md) | 正式材料、质量核验与提交记录 |
| [docs/project-plan.md](docs/project-plan.md) | 历史计划及专项学习资料，执行日期见新分工表 |
| [docs/topic-analysis.md](docs/topic-analysis.md) | 历史选题比较与综合评价 |
| [docs/team-review.md](docs/team-review.md) | 三人独立评价、试做记录与决策表 |
| [docs/sources.md](docs/sources.md) | 规则与技术资料来源、已知限制 |
| [docs/ai-usage.md](docs/ai-usage.md) | AI 辅助工作记录及后续填写模板 |
| [CONTRIBUTING.md](CONTRIBUTING.md) | 讨论、分支、PR 与证据记录方式 |
| [.github/ISSUE_TEMPLATE](.github/ISSUE_TEMPLATE) | 候选题讨论、验证任务模板 |

## 许可

本仓库原创文档采用 [CC BY-SA 4.0](LICENSE)，程序代码采用 [MIT](LICENSE-CODE)。第三方资料及引用内容保留原许可。

最近更新：**2026-11-16（Asia/Shanghai）**。赛事动态以官方平台最新公告为准。
