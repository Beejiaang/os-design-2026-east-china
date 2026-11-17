# 开发时间线

日期按提交记录；只列已有材料和执行证据，不据此认领成员人工贡献。Git 提交链接固定历史，源码和实测阶段各自说明。

| 日期 | 事件与提交 | 原始证据 / 过程记录 |
|---|---|---|
| 2026-10-20 | 初始化并分析八类选题：[19ee159](https://github.com/Beejiaang/os-design-2026-east-china/commit/19ee159)、[9360d9b](https://github.com/Beejiaang/os-design-2026-east-china/commit/9360d9b) | [选题分析](topic-analysis.md)、[AI 记录](../records/ai-usage.md)；此时无运行证据 |
| 2026-10-21 | 确定方向 A 的收窄范围和三人排期：[686b083](https://github.com/Beejiaang/os-design-2026-east-china/commit/686b083) | [历史计划](project-plan.md)、[AI 记录](../records/ai-usage.md)；计划不等于已实现 |
| 2026-11-16 | feat/member-a-runner：执行/采集初版 de34b8c，兼容强化 02f5c65，中断恢复 9c075aa；最终证据 [63bd225](https://github.com/Beejiaang/os-design-2026-east-china/commit/63bd225) | [A 验证](../validation/member-a-validation.md)、[A 归档哈希](../../evidence/member-a/SHA256SUMS)、[AI 记录](../records/ai-usage.md)；17 项测试、12 次三档执行，异常另列 |
| 2026-11-17 | feat/bc-end-to-end：固定输入、SQLite 校验、分析与报告接通；[537027e](https://github.com/Beejiaang/os-design-2026-east-china/commit/537027e) 归档 | [集成验证](../validation/pipeline-validation.md)、[集成哈希](../../evidence/integration/SHA256SUMS)、[AI 记录](../records/ai-usage.md)；openEuler 与 WSL 分开保留 |
| 2026-11-17 | feat/b-comparison-validation：原生工具对照、规则边界与范围敏感性；[57c865e](https://github.com/Beejiaang/os-design-2026-east-china/commit/57c865e) | [对照验证](../validation/comparison-validation.md)、[对照哈希](../../evidence/comparison/SHA256SUMS)、[AI 记录](../records/ai-usage.md)；36+48 次真实执行 |
| 2026-11-17 | feat/c-defense-reproduction：工作稿、人员复验指南与源码复验包；[2697479](https://github.com/Beejiaang/os-design-2026-east-china/commit/2697479) | [安装复验](../validation/reproduction-validation.md)、[复验哈希](../../evidence/reproduction/SHA256SUMS)、[AI 记录](../records/ai-usage.md)；代理检查，非人员验收 |
| 2026-11-17 | feat/a-release-preparation：086aff7 冻结复验，30e6a31 归档；[309a85f](https://github.com/Beejiaang/os-design-2026-east-china/commit/309a85f) 发布候选材料；main 的 [54ef928](https://github.com/Beejiaang/os-design-2026-east-china/commit/54ef928) 集成 | [RC1 验证](../validation/release-validation.md)、[冻结哈希](../../evidence/release/SHA256SUMS)、[AI 记录](../records/ai-usage.md)；29 项 0 跳过、18 次完整流程，未正式提交 |

后续逐项改进记录见[交接](../handoff/agent-handoff.md)，不改写上述冻结材料或原始数据。分支名称描述当时演进，当前分支以 git branch --show-current 为准。
