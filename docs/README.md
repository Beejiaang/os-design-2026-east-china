# 文档导航

所有命令默认从仓库根目录运行。Agent 从 [AGENTS.md](../AGENTS.md) 开始；本文按用途划分文档，避免把历史方案当当前接口。

| 分区 | 入口 | 用途 |
|---|---|---|
| 项目约定 | [统一口径](project/project-contract.md)、[分工计划](project/work-allocation.md)、[提交清单](project/submission-checklist.md) | 做什么、谁负责、阶段和正式交付条件 |
| 数据协议 | [数据协议](contracts/data-contract.md) | 字段、状态、单位、版本和恢复语义；机器格式在 schemas/ |
| 实现说明 | [成员 A](implementation/member-a.md)、[聚合与报告流程](implementation/pipeline.md)、[系统设计](implementation/system-design.md) | 执行器、独立校验、分析、离线报告 |
| 验证记录 | [A 的实测记录](validation/member-a-validation.md)、[完整流程验证](validation/pipeline-validation.md) | 对应提交、环境、命令与原始证据 |
| Agent 交接 | [当前状态与角色启动任务](handoff/agent-handoff.md) | A/B/C 输入输出、可复制任务和交接模板 |
| 过程与来源 | [AI 使用记录](records/ai-usage.md)、[资料来源](records/sources.md) | 过程披露、来源与限制 |
| 历史资料 | [旧计划](history/project-plan.md)、[选题分析](history/topic-analysis.md)、[讨论模板](history/team-review.md) | 保留决策过程，不覆盖当前计划和协议 |

文件存放边界见 [工程分区规则](project/directory-layout.md)。新增文档放到相应分区，并补充本页或对应交接入口，不在 docs 根目录继续平铺。
