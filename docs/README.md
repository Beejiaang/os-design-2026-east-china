# 文档导航

所有命令默认从仓库根目录运行。Agent 从 [AGENTS.md](../AGENTS.md) 开始；本文按用途划分文档，避免把历史方案当当前接口。

| 分区 | 入口 | 用途 |
|---|---|---|
| 项目约定 | [统一口径](project/project-contract.md)、[分工计划](project/work-allocation.md)、[提交清单](project/submission-checklist.md) | 做什么、谁负责、阶段和正式交付条件 |
| 数据协议 | [数据协议](contracts/data-contract.md) | 字段、状态、单位、版本和恢复语义；机器格式在 schemas/ |
| 候选交付 | [设计测试总稿](implementation/design-and-test-report.md)、[版本核验](validation/release-validation.md)、[平台准备](project/platform-readiness.md) | 工程与材料的版本对应、已检查范围和外部阻碍 |
| 实现说明 | [成员 A](implementation/member-a.md)、[聚合与报告流程](implementation/pipeline.md)、[系统设计](implementation/system-design.md)、[同类工具对照](implementation/tool-comparison.md) | 执行器、独立校验、分析、离线报告、贡献边界 |
| 验证记录 | [A 的实测记录](validation/member-a-validation.md)、[完整流程验证](validation/pipeline-validation.md)、[扩展对照与边界验证](validation/comparison-validation.md) | 对应提交、环境、命令与原始证据 |
| 安装与人员复验 | [新环境安装记录](validation/reproduction-validation.md)、[人员复验指南](validation/peer-reproduction.md)、[空白模板](validation/peer-review-template.md) | 区分代理安装检查与真实非实现者验收 |
| 演示交付 | [十页答辩稿](../demo/presentation/答辩初稿_20261117_v1.pptx)、[讲解与20问](../demo/defense-notes.md)、[复验包](../demo/delivery/README.md) | 演示、讲解与交接，不代表正式视频或平台提交 |
| Agent 交接 | [当前状态与角色启动任务](handoff/agent-handoff.md) | A/B/C 输入输出、可复制任务和交接模板 |
| 过程与来源 | [AI 使用记录](records/ai-usage.md)、[资料来源](records/sources.md) | 过程披露、来源与限制 |
| 历史资料 | [旧计划](history/project-plan.md)、[选题分析](history/topic-analysis.md)、[讨论模板](history/team-review.md) | 保留决策过程，不覆盖当前计划和协议 |

文件存放边界见 [工程分区规则](project/directory-layout.md)。新增文档放到相应分区，并补充本页或对应交接入口，不在 docs 根目录继续平铺。

本轮改进：[P0任务进度](validation/improvement-progress.md)、[评审导读](reviewers-guide.md)、[开发时间线](history/timeline.md)、[材料版本对应表](validation/material-versions.md)。

P1本轮：[执行进度](validation/improvement-p1-progress.md)、[目标机复验与规模实测](validation/improvement-p1-validation.md)、[统一术语表](contracts/glossary.md)。

P2本轮：[执行进度与总状态](validation/improvement-p2-progress.md)、[CHANGELOG](../CHANGELOG.md)。任务21按迁移前提未成立保持文件名。
