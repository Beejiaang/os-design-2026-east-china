# Agent 交接与当前状态

日期：2026-11-17。先读根目录 `AGENTS.md`、[统一口径](../project/project-contract.md)、[数据协议](../contracts/data-contract.md)。本页是接续入口；实测细节和 commit 以验证记录与 Git 为准。

**当前接续：`feat/b-comparison-validation`。** 用户要求继续推进同类对照与规则扩展。此分支基于 `d649f7f`，测量源码 `8d76aed`，最终派生诊断/报告源码 `25b7f32`；29 项目标机测试通过，新增 36 次原生对照及 48 次边界实验。见 [对照方法](../implementation/tool-comparison.md)、[扩展验证](../validation/comparison-validation.md)。未推送/建 PR/合并。

上一轮新增 B/C 与集成代码在本地 `feat/bc-end-to-end`，基于 `a0d6edd`；不要从零重写负载和报告。初轮负载测量源码为 `2ac22b7`；元数据异常处理修正与分析为 `1028dd8`，证据见 [初轮集成验证](../validation/pipeline-validation.md)。原始数据提交不改写。

交付时 Windows 原工程与 openEuler 原开发目录 `/home/holo/projects/os-design-2026-east-china` 同步到当前分支；原 A/B/C 首轮分支保留。初轮实验位于 `/home/holo/projects/osdesign-integration-20261117/results`，本轮位于 `/home/holo/projects/osdesign-comparison-20261117/results`；共享归档分别在 evidence/integration 与 evidence/comparison。独立复验检出不是另一份主工程。

## 先找到正确代码

A 首轮实现和协作规则的集成分支为 `feat/member-a-runner`。未合入 main 时，直接从 main 开始会缺少 runner/collector。先 fetch、查看该分支和 PR，再按角色创建自己的分支：

```bash
git fetch origin
git switch -c feat/b-group-aggregation origin/feat/member-a-runner
# C 可用 feat/c-analysis-report；不要重复创建已存在的同名分支
```

如果已有工作目录/未提交改动，先保存并检查，不能直接照抄切换命令覆盖工作。合并后从更新的 main 创建新分支即可。不要默认本机 SSH 别名、地址、私钥、盘符或虚拟机已在队友电脑配置。

## 当前角色状态

| 角色 | 已有输入/产物 | 下一项任务 | 当前阻碍/不能宣称的完成 |
|---|---|---|---|
| A | 执行、采集、异常/恢复、run 1.1；已接 B/C，核验最终记录和清理 | 配合非实现者复验；审查新接口变动 | 不代替人员交叉验收或整阶段验收 |
| B | 固定输入/独立校验；首轮 54 次、本轮 84 次目标机执行；GNU time+systemd-run 正常场景对照；额外 5/15/25% 样本 | 非实现者复验、更多机器/波动样本、其他完整框架对照评估 | 不宣称真实生产退化事故、普遍准确率或已覆盖全部同类工具 |
| C | 结构/完整性、排除原因、配置对照、历史前提、探索性信号、范围敏感性、离线 HTML 追溯 | 浏览器视觉核验、更广规则验收、最终视频/PPT | 范围敏感性不是置信区间；代理实测不等于人工作业验收 |

A 的中断与清理状态有测试，正式性能基线还需要足够实验设计、B 的功能验证和 C 的规则。系统异常测试不替代负载测试。

最近实际验证的实现提交是 `9c075aa9031ea3b699dbf22b1b2bd7d9b94f38b4`；之后的验证说明/样例/证据提交不改变执行器代码。17 项目标机测试、12 次正常实验及 5 份故障注入最终记录见 [A 验证记录](../validation/member-a-validation.md)。可直接读取 [真实 1.1 样例](../../examples/measured-run-1.1.json) 接通解析，完整原始目录在 stage3 归档；不要把该单条样例当足够的统计验收样本。

## 旧角色启动模板（保留职责边界，当前应接续现有实现）

以下模板写于 B/C 未实现时。当前首先核对上面的最新交付与源码；把“实现”改为审查/复验/必要修正，不重复建另一套工程。

### B 给 Agent 的启动任务

> 你负责本仓库成员 B。先读 AGENTS.md、docs/project/project-contract.md、docs/contracts/data-contract.md、docs/project/work-allocation.md、docs/handoff/agent-handoff.md，并检查分支和已有改动。以当前 A 集成分支/已合并 main 为依赖，实现固定种子、规模可调的输入生成及单进程分组聚合；输出应确定且可被独立参考算法验证。代码放 workloads，配置/实验放 experiments，增加本角色必要测试。不改 runner 的字段、单位、状态或计时语义。提供 workload_version、可追溯 input_id 和 argv；用 A 执行器接入三档实验，保存真实输出、功能校验和限制。不要把故障夹具当 measured 性能数据，不替 C 生成回归结论。完成后按本页模板交接并更新 AI 使用记录；未获用户授权不推送/合并。

### C 给 Agent 的启动任务

> 你负责本仓库成员 C。先读 AGENTS.md、docs/project/project-contract.md、docs/contracts/data-contract.md、docs/project/work-allocation.md、docs/handoff/agent-handoff.md，并检查分支和已有改动。基于 A 的 run 1.1 最终记录实现 src/analysis 与 src/report：先校验版本/结构与整轮完整性，区分失败、缺失、中断、恢复、模拟和预热；做同任务不同配额的描述性配置对照及离线 HTML，数字按 run_id 追溯。历史比较先调用 runner.compatibility.check_compatibility，前提不符显示无法比较原因；不能输出“无退化”。B 正确性或样本证据不足时明确列出，不凭 stdout 哈希宣称功能正确。不改原始数据或 A 的测量/状态语义。用真实数据核对报告，保留误差和局限。完成后按本页模板交接并更新 AI 使用记录；未获用户授权不推送/合并。

## A 给后续 Agent 的接续任务（可复制）

> 你负责成员 A 的系统与集成。先读 AGENTS.md、统一口径、数据协议、A 的实现与验证记录，确认当前提交和工作树；不要重复已通过的工作。优先检查 B/C 是否已交付以及是否改变接口。联调 B 的固定输入/正确性校验，核对 C 的样本分类、指标单位、run_id 原始数字和无法比较提示。新增公共接口必须版本化并附迁移与测试，不能把前提兼容当作统计判定。仅控制本工具的临时服务，保留异常与清理证据。非实现者验收、平台提交等尚无证据的事项继续标待完成。

## 单次交接模板

```text
角色和目标：
基于分支 / 基于 commit：
交付 commit / PR（尚未提交时写 dirty）：
修改路径和模块边界：
协议版本、兼容变化、对方要迁移什么：
依赖 / 安装 / 最短运行命令（相对项目根目录）：
实际执行的环境、命令、结果：
证据路径、原始输入/输出及校验值：
尚未执行的测试 / 被跳过的测试：
已知限制、失败和修正：
已推送 / 已建 PR / 已合并 / 正式提交状态（分别填写）：
下一位需要做的具体动作和阻碍：
人工复核 / 非实现者复现状态：
```

不要填猜测的队友姓名或贡献；不要附凭据、完整私人聊天或本机专属密钥路径。阶段完成只能由该阶段所有所需证据支持。

## 队友复现验收（待执行，不预勾）

- [ ] 非实现者拉取指定提交并记录自身环境、操作者与时间
- [ ] 理解 doctor、三档配额、运行结果、失败/中断与 recover 的不同语义
- [ ] 执行 README 示例和本角色测试，保留真实命令与日志
- [ ] 对 B 的确定性输出进行独立校验，并让 C 的报告可追溯到 run_id
- [ ] 记录差异/问题并复验修复；确认不是把同一代理复验标成人员交叉验收
