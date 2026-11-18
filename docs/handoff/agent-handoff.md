# 最新接续：目标机节流证据与缺样本复核

2026-11-18，角色 C 分析与报告，基于 f7dca19，在本地 feat/c-quota-coverage 上完成。测量源码 5a5e109，39 项系统环境测试及四轮默认流程通过。原始 run 1.1 沿用；消费配置汇总时需允许零样本档的指标为空。同一登录会话可复验历史对照；跨 SSH 会话的指纹拒绝实例已归档。命令、教学案例、原始数据及缺项见[本轮验证](../validation/quota-evidence.md)。RC2 仍为上一版候选包，人员复验、演示视频与正式提交待团队完成。

# 最新接续：RC2材料同步

2026-11-17，基于7ef8f88，当前串联分支improve/22-current-materials。9页报告Word/PDF和12页可编辑PPT已纳入P0/P1/P2；独立RC2 manifest保存哈希，RC1原文件/标签不变。最终RC2包固定源码`70580dc968edeba6e24cea14d240fdf45904d9a3`，157份文件哈希、新bundle克隆和双版本材料声明通过；报告9页、PPT12页。详见[本轮核验](../validation/release-validation-rc2.md)及[交付入口](../../demo/delivery/README.md)。原测量源码bb288cb等分别注明，未重标为材料提交。

本轮不改运行代码，仅作者/打包/材料表工具及材料文档；未推送、未建PR、未合并、未创建标签，人员/视频/平台仍待完成。下方“旧RC1未重生成/材料未更新”为历史记录，以本段新增RC2材料为准，旧文件本身仍不覆盖。

# 最新接续：Tasklist P2 已处理

2026-11-17：基于19b223f，当前本地串联分支 **improve/21-delivery-name-policy**，包含全部P0/P1及本轮P2文档；main仍为54ef928。任务20在7360e66补齐CHANGELOG及标签建议；任务21在030ba00复核迁移条件未成立，保持交付文件名。详见[P2进度与限制](../validation/improvement-p2-progress.md)。

本地既有注释标签v0.1.0-rc.1仍指向54ef928；本轮未创建、移动、删除或推送标签，未执行推送/PR/合并/正式提交。运行代码和旧RC1材料/证据未变，仅文档链接、版本事实与哈希检查；最新运行验证仍见下方P1。旧材料未重生成、GitHub在线CI、人员/视频/平台事项仍未完成。下方P0/P1“P2未执行”是当时历史状态，以本段为准。

# 最新接续：Tasklist P1 已执行

2026-11-17：用户授权继续下一轮，当前本地串联分支 **improve/10-scale-sweep**，包含全部P0/P1；起点本轮44dbddd，main未改。P1各任务分支与提交见[进度报告](../validation/improvement-p1-progress.md)。六个代码任务分别完成干净源码目标机复验，最后测量源码bb288cb为37项0跳过、默认完整流程18次与Ruff/pip check通过；另有规模扫描54次全量独立校验通过。证据和边界见[P1验证](../validation/improvement-p1-validation.md)。

run1.1/config1.0字段不变，附加linux-load-v1证据和src-py-v2算法在协议中明确；旧指纹数据不重写，新旧摘要不可混比。早期各任务“待目标机验证”以本段和逐提交验证表的实际结果更新；以下P0/RC1条目为历史。

未推送、未建PR、未合并回main、未打tag、未正式提交。P2未执行；人工/视频事项未代办，旧RC1二进制材料未重生成。

# 最新接续：Tasklist P0 已执行

2026-11-17：当前本地串联分支 **improve/09-gitlab-copy**，包含任务1–9；起点main / 54ef928，main未改。各任务分支/提交/路径与检查见[完整进度](../validation/improvement-progress.md)，本轮各任务交接在文末。运行测量源码d8a331e，CI/清单最终代码源码a4f4c04，两者均在openEuler完成29项0跳过、默认18次完整流程及pip check；新增工具对照54次全部通过。材料表脚本独立生成，旧RC1二进制不重生成。

CI仅本地/目标机手动等价命令验证，未运行GitHub在线矩阵。本轮未推送、未建PR、未合并回main、未打tag、未正式提交；P1待下一轮。下方“当前候选/当前接续”均为RC1历史交接，不能覆盖本段。人员与视频事项继续待人工。

# 当前候选交付更新

完整集成入口：[PR3](https://github.com/Beejiaang/os-design-2026-east-china/pull/3)；原A的PR2已合并。候选ZIP、七页Word/PDF、十页PPT及原始证据见[交付入口](../../demo/delivery/README.md)，源码快照30e6a31，目标机冻结复验086aff7，29项0跳过与18次完整流程通过。后续从已合并的main或当前集成分支接续，先fetch并核对PR实际状态；不要照下文历史A首轮启动模板重复实现B/C。

2026-11-17：用户要求除人工验收和视频演示外继续完成其余事项。本轮角色为A集成，范围覆盖正式技术稿、PPT原生检查、冻结复验、交付包与仓库整合。当前分支feat/a-release-preparation，基于2697479；运行逻辑未改，旧分支和原始记录保留。正式设计稿与平台缺项见[候选验证](../validation/release-validation.md)、[平台准备](../project/platform-readiness.md)。下文历史“未推送”“PPT未原生检查”以本段及候选验证为准；人员与视频未代办。

# Agent 交接与当前状态

日期：2026-11-17。先读根目录 `AGENTS.md`、[统一口径](../project/project-contract.md)、[数据协议](../contracts/data-contract.md)。本页是接续入口；实测细节和 commit 以验证记录与 Git 为准。

**当前接续：`feat/c-defense-reproduction`。** 基于 `57c865e`，本轮没有改运行实现。新增十页答辩工作稿、讲解与20问、人员复验指南/空白模板和固定源码复验包；新源码检出/全新 venv 完成可编辑安装、29 项测试及三档小试，见 [安装复验](../validation/reproduction-validation.md)。尚未非实现者验收、正式视频/平台提交或推送/PR/共享合并。

上轮对照分支 `feat/b-comparison-validation` 基于 `d649f7f`，测量源码 `8d76aed`，最终派生诊断/报告源码 `25b7f32`；29 项目标机测试通过，新增 36 次原生对照及 48 次边界实验。见 [对照方法](../implementation/tool-comparison.md)、[扩展验证](../validation/comparison-validation.md)。当前复验包故意固定该轮完整快照 57c865e，材料另行标工作稿。

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
| C | 分析/报告、范围敏感性、十页可编辑答辩稿与备注、讲解20问、人员复验指南/包 | 浏览器视觉核验、更广规则验收、正式视频与最终答辩规格 | PPT 是工作稿，已完成代理 PowerPoint 原生逐页版式检查；代理实测不等于人工作业验收 |

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

## 改进任务 2：固定样本阈值矩阵（2026-11-17）

角色：A 集成，用户授权按 tasklist 跨角色推进。基于 `54ef9281905b5316010b5484d62795fb8fb092ab`；分支 `improve/02-threshold-matrix`，交付提交见该分支 Git HEAD（避免自引用哈希）。

- 修改范围：docs/validation/comparison-validation.md、evidence/comparison/threshold-matrix-20261117.json、evidence/comparison/SHA256SUMS。run 1.1 / config 1.0 不变，无消费者迁移。
- 验证：重新分析六场景共 48 条记录；15 格可比，逐格保留 run_id；Markdown 链接检查通过。
- 状态：仅本地提交；未推送、未建 PR、未合并、未正式提交；非实现者验收仍待人工。

## 改进任务 1：hyperfine 三档实测对照（2026-11-17）

角色：A 集成，用户授权按 tasklist 跨角色推进。基于 `6f6fb7d`；分支 `improve/01-hyperfine`，交付提交见该分支 Git HEAD（避免自引用哈希）。

- 修改范围：docs/implementation/tool-comparison.md、docs/validation/comparison-validation.md、evidence/comparison/improve01-openeuler-20261117.tar.gz、evidence/comparison/SHA256SUMS。run 1.1 / config 1.0 不变，无消费者迁移。
- 验证：干净源码 d8a331e：openEuler 29 项0跳过；默认完整流程18次；对照54次逐份SQLite/配额/清理通过；pip check通过。证据 evidence/comparison/improve01-openeuler-20261117.tar.gz。
- 状态：仅本地提交；未推送、未建 PR、未合并、未正式提交；非实现者验收仍待人工。

## 改进任务 3：评审三份材料导读（2026-11-17）

角色：A 集成，用户授权按 tasklist 跨角色推进。基于 `4f8ca84cc54a75d38f45019354e54d871d7082f5`；分支 `improve/03-reviewers-guide`，交付提交见该分支 Git HEAD（避免自引用哈希）。

- 修改范围：docs/reviewers-guide.md、README.md。run 1.1 / config 1.0 不变，无消费者迁移。
- 验证：本地 Markdown 链接检查通过；导读正文为一张五行索引表。
- 状态：仅本地提交；未推送、未建 PR、未合并、未正式提交；非实现者验收仍待人工。

## 改进任务 4：可追溯开发时间线（2026-11-17）

角色：A 集成，用户授权按 tasklist 跨角色推进。基于 `31f6f2875353a330e3a0e2229701441badaef517`；分支 `improve/04-timeline`，交付提交见该分支 Git HEAD（避免自引用哈希）。

- 修改范围：docs/history/timeline.md、README.md。run 1.1 / config 1.0 不变，无消费者迁移。
- 验证：git log --all 核对日期和提交；本地文档与 evidence 链接检查通过。
- 状态：仅本地提交；未推送、未建 PR、未合并、未正式提交；非实现者验收仍待人工。

## 改进任务 5：教学观察思考题与报告模板（2026-11-17）

角色：A 集成，用户授权按 tasklist 跨角色推进。基于 `1d54111cb4b752cdd2fd89045fb3763b9a0557ac`；分支 `improve/05-teaching-observations`，交付提交见该分支 Git HEAD（避免自引用哈希）。

- 修改范围：docs/implementation/teaching-experiments.md。run 1.1 / config 1.0 不变，无消费者迁移。
- 验证：原有 bash 命令逐字保留；数值核对集成验证表；本地链接检查通过。
- 状态：仅本地提交；未推送、未建 PR、未合并、未正式提交；非实现者验收仍待人工。

## 改进任务 6：最小纯单元与协议 CI（2026-11-17）

角色：A 集成，用户授权按 tasklist 跨角色推进。基于 `4ccef588fe312adfb3e411dff5f041cfa12221ac`；分支 `improve/06-ci`，交付提交见该分支 Git HEAD（避免自引用哈希）。

- 修改范围：.github/workflows/ci.yml。run 1.1 / config 1.0 不变，无消费者迁移。
- 验证：workflow 已准备；无推送授权，GitHub 未运行。最终本地/目标机等价命令日志统一归档到 P0 验证记录；不把跳过系统项计为通过。tasklist 中任务6所指 ruff 实为任务17，本轮不提前机械修改源码。
- 状态：仅本地提交；未推送、未建 PR、未合并、未正式提交；非实现者验收仍待人工。

## 改进任务 7：仓库体积及大文件评估（2026-11-17）

角色：A 集成，用户授权按 tasklist 跨角色推进。基于 `c65611aff4830316bb082c87122e0f3c172973b3`；分支 `improve/07-repository-size`，交付提交见该分支 Git HEAD（避免自引用哈希）。

- 修改范围：docs/project/platform-readiness.md。run 1.1 / config 1.0 不变，无消费者迁移。
- 验证：git count-objects -vH 与 git ls-files -z + stat 实测；所有表项按字节记；未迁移文件或改写历史。
- 状态：仅本地提交；未推送、未建 PR、未合并、未正式提交；非实现者验收仍待人工。

## 改进任务 8：材料版本与哈希自动清单（2026-11-17）

角色：A 集成，用户授权按 tasklist 跨角色推进。基于 `1e1a83f`；分支 `improve/08-material-manifest`，交付提交见该分支 Git HEAD（避免自引用哈希）。

- 修改范围：scripts/material_manifest.py、docs/validation/material-versions.md、docs/validation/improvement-p0-validation.md、evidence/improvement。run 1.1 / config 1.0 不变，无消费者迁移。
- 验证：脚本源码a4f4c04；两次生成逐字节一致、冻结材料错误哈希夹具被拒绝；openEuler29项0跳过+完整流程18次+pip check通过。本地3.12纯测试20通过9跳过。见docs/validation/improvement-p0-validation.md。
- 状态：仅本地提交；未推送、未建 PR、未合并、未正式提交；非实现者验收仍待人工。

## 改进任务 9：GitLab 命名与描述文案草稿（2026-11-17）

角色：A 集成，用户授权按 tasklist 跨角色推进。基于 `29b660f69748a6beac66ded3ed7ad91a5cabffa4`；分支 `improve/09-gitlab-copy`，交付提交见该分支 Git HEAD（避免自引用哈希）。

- 修改范围：docs/project/platform-readiness.md。run 1.1 / config 1.0 不变，无消费者迁移。
- 验证：核对用户提供技术方案第四部分本地缓存；必需五项字段齐全，保留人工填空；链接检查通过。
- 状态：仅本地提交；未推送、未建 PR、未合并、未正式提交；非实现者验收仍待人工。

## 改进任务 12：重复次数与预热依据（2026-11-17）

角色：A 集成，用户授权按 tasklist 跨角色推进。基于 `44dbdddefdf04e3163c5169497e25ee92d8594a0`；分支 `improve/12-sampling-rationale`，交付提交见该分支 Git HEAD（避免自引用哈希）。

- 修改范围：docs/implementation/pipeline.md。run 1.1 / config 1.0 不变，无消费者迁移。
- 验证：文档事实核对与本地链接检查；未更改运行代码。
- 状态：仅本地提交；未推送、未建 PR、未合并、未正式提交；非实现者验收仍待人工。

## 改进任务 15：README三行状态头（2026-11-17）

角色：A 集成，用户授权按 tasklist 跨角色推进。基于 `0df6e0d3f712cbe30de3899ac2e874a681fc240f`；分支 `improve/15-readme-status`，交付提交见该分支 Git HEAD（避免自引用哈希）。

- 修改范围：README.md。run 1.1 / config 1.0 不变，无消费者迁移。
- 验证：文档事实核对与本地链接检查；未更改运行代码。
- 状态：仅本地提交；未推送、未建 PR、未合并、未正式提交；非实现者验收仍待人工。

## 改进任务 16：资源计时和完成状态统一术语（2026-11-17）

角色：A 集成，用户授权按 tasklist 跨角色推进。基于 `be858343a17f176814fba21352201f12a2a267a9`；分支 `improve/16-glossary`，交付提交见该分支 Git HEAD（避免自引用哈希）。

- 修改范围：docs/contracts/glossary.md、README.md、docs/implementation/pipeline.md、docs/implementation/member-a.md、docs/implementation/system-design.md、docs/implementation/tool-comparison.md。run 1.1 / config 1.0 不变，无消费者迁移。
- 验证：文档事实核对与本地链接检查；未更改运行代码。
- 状态：仅本地提交；未推送、未建 PR、未合并、未正式提交；非实现者验收仍待人工。

## 改进任务 19：核心冻结后变更规则（2026-11-17）

角色：A 集成，用户授权按 tasklist 跨角色推进。基于 `b0aa997431308138378786f5c87591e3e75bb46b`；分支 `improve/19-freeze-policy`，交付提交见该分支 Git HEAD（避免自引用哈希）。

- 修改范围：AGENTS.md。run 1.1 / config 1.0 不变，无消费者迁移。
- 验证：文档事实核对与本地链接检查；未更改运行代码。
- 状态：仅本地提交；未推送、未建 PR、未合并、未正式提交；非实现者验收仍待人工。

## 改进任务 17：Ruff默认规则与CI接入（2026-11-17）

角色：A 集成，用户授权按 tasklist 跨角色推进。基于 `0e30e7f`；分支 `improve/17-ruff`，交付提交见该分支 Git HEAD（避免自引用哈希）。

- 修改范围：pyproject.toml、.github/workflows/ci.yml、src/report/html.py、tests/test_member_a.py。run 1.1 / config 1.0 不变，无消费者迁移。
- 验证：Ruff0.17.5默认E4/E7/E9/F规则通过；只删除一个未用import及将两个lambda机械改成def。本地29项20通过9跳过；因src改动，目标机全量验证在本轮证据记录中补齐，未据此宣称目标机通过。
- 状态：仅本地提交；未推送、未建 PR、未合并、未正式提交；非实现者验收仍待人工。

## 改进任务 18：复用report extra并加入开发检查（2026-11-17）

角色：A 集成，用户授权按 tasklist 跨角色推进。基于 `f96e456`；分支 `improve/18-extras`，交付提交见该分支 Git HEAD（避免自引用哈希）。

- 修改范围：pyproject.toml、docs/implementation/pipeline.md。run 1.1 / config 1.0 不变，无消费者迁移。
- 验证：Windows3.12 editable安装.[dev]及pip check通过；report extra保留为唯一jsonschema声明。目标机全量验证待本轮归档；不改变执行器依赖。
- 状态：仅本地提交；未推送、未建 PR、未合并、未正式提交；非实现者验收仍待人工。

## 改进任务 11：Linux负载旁路采样（2026-11-17）

角色：A 集成，用户授权按 tasklist 跨角色推进。基于 `5e0a9d9`；分支 `improve/11-host-load`，交付提交见该分支 Git HEAD（避免自引用哈希）。

- 修改范围：src/collector/host_load.py、src/runner/core.py、tests/test_host_load.py、docs/contracts/data-contract.md。run 1.1 / config 1.0 不变，无消费者迁移。
- 验证：新增3项采样/异常/写入失败单测；本地32项23通过9跳过，Ruff通过；目标机全量和完整流程按此源码单独复验归档。environment.json附加证据格式linux-load-v1，run/config不变，采样不参与判定。
- 状态：仅本地提交；未推送、未建 PR、未合并、未正式提交；非实现者验收仍待人工。

## 改进任务 13：历史比较观察范围区间条（2026-11-17）

角色：A 集成，用户授权按 tasklist 跨角色推进。基于 `1bde76a`；分支 `improve/13-range-visualization`，交付提交见该分支 Git HEAD（避免自引用哈希）。

- 修改范围：src/report/html.py、tests/test_range_bar.py。run 1.1 / config 1.0 不变，无消费者迁移。
- 验证：新增2项SVG几何/缺失数据测试；本地34项25通过9跳过，Ruff通过。原compare未改；目标机全量及真实数据重生成截图待本轮验证归档。
- 状态：仅本地提交；未推送、未建 PR、未合并、未正式提交；非实现者验收仍待人工。

## 改进任务 14：全src长度分帧源码指纹（2026-11-17）

角色：A 集成，用户授权按 tasklist 跨角色推进。基于 `2d60a88`；分支 `improve/14-source-fingerprint`，交付提交见该分支 Git HEAD（避免自引用哈希）。

- 修改范围：src/runner/core.py、tests/test_source_fingerprint.py、schemas/run-1.1.schema.json、docs/contracts/data-contract.md、docs/implementation/member-a.md。run 1.1 / config 1.0 不变，无消费者迁移。
- 验证：新增2项路径/嵌套文件/内容分界测试；本地36项27通过9跳过，Ruff通过。src-py-v2算法版本在域分隔和协议中显式说明；run1.1字段形状不变，新旧指纹不可混比。目标机逐源码复验待归档。
- 状态：仅本地提交；未推送、未建 PR、未合并、未正式提交；非实现者验收仍待人工。

## 改进任务 10：三种规模独立正确性及内存实测（2026-11-17）

角色：A 集成，用户授权按 tasklist 跨角色推进。基于 `0be73a7`；分支 `improve/10-scale-sweep`，交付提交见该分支 Git HEAD（避免自引用哈希）。

- 修改范围：experiments/scale_sweep.py、tests/test_scale_sweep.py、docs/validation/improvement-p1-validation.md、evidence/improvement。run 1.1 / config 1.0 不变，无消费者迁移。
- 验证：bb288cb：openEuler37项0跳过+默认18次完整流程+pip check+Ruff；规模扫描54次逐份SQLite/配额/内存/清理通过。六个代码任务分别复验的日志、源码与限制见docs/validation/improvement-p1-validation.md。
- 状态：仅本地提交；未推送、未建 PR、未合并、未正式提交；非实现者验收仍待人工。

### 任务17目标机验收补记

干净源码`f96e456`：openEuler 29项测试0跳过、默认18次完整流程、Ruff与pip check均通过，末尾临时单元为零。真实日志、命令及证据见[P1验证](../validation/improvement-p1-validation.md)，原始归档未重写。协议/迁移以数据协议为准；仅本地提交，人员验收待人工。

### 任务18目标机验收补记

干净源码`5e0a9d9`：openEuler 29项测试0跳过、默认18次完整流程、Ruff与pip check均通过，末尾临时单元为零。真实日志、命令及证据见[P1验证](../validation/improvement-p1-validation.md)，原始归档未重写。协议/迁移以数据协议为准；仅本地提交，人员验收待人工。

### 任务11目标机验收补记

干净源码`1bde76a`：openEuler 32项测试0跳过、默认18次完整流程、Ruff与pip check均通过，末尾临时单元为零。真实日志、命令及证据见[P1验证](../validation/improvement-p1-validation.md)，原始归档未重写。协议/迁移以数据协议为准；仅本地提交，人员验收待人工。

### 任务13目标机验收补记

干净源码`2d60a88`：openEuler 34项测试0跳过、默认18次完整流程、Ruff与pip check均通过，末尾临时单元为零。真实日志、命令及证据见[P1验证](../validation/improvement-p1-validation.md)，原始归档未重写。协议/迁移以数据协议为准；仅本地提交，人员验收待人工。

### 任务14目标机验收补记

干净源码`0be73a7`：openEuler 36项测试0跳过、默认18次完整流程、Ruff与pip check均通过，末尾临时单元为零。真实日志、命令及证据见[P1验证](../validation/improvement-p1-validation.md)，原始归档未重写。协议/迁移以数据协议为准；仅本地提交，人员验收待人工。

## 改进任务 20：变更日志与候选标签建议（2026-11-17）

角色：A 集成，用户授权按 tasklist 跨角色推进。基于 `19b223f17f343596f6a2f5b17b6f520d2a96f7ce`；分支 `improve/20-changelog`，交付提交见该分支 Git HEAD（避免自引用哈希）。

- 修改范围：CHANGELOG.md、README.md、docs/project/platform-readiness.md。run 1.1 / config 1.0 不变，无消费者迁移。
- 验证：读取Git历史、pyproject旧版本及现有注释标签核对；本地Markdown链接检查通过。仅文档变更，不重跑目标机测试，不创建或修改标签。
- 状态：仅本地提交；未推送、未建 PR、未合并、未正式提交；非实现者验收仍待人工。

## 改进任务 21：交付改名条件复核并保持现状（2026-11-17）

角色：A 集成，用户授权按 tasklist 跨角色推进。基于 `7360e66bf97bc60878ef23e49438b8891e1f9406`；分支 `improve/21-delivery-name-policy`，交付提交见该分支 Git HEAD（避免自引用哈希）。

- 修改范围：docs/project/platform-readiness.md。run 1.1 / config 1.0 不变，无消费者迁移。
- 验证：实际重测tracked字节36,731,608，对象库测量已记入平台准备；未发生大文件迁移，按清单条件不执行改名。仅文档及链接检查，无运行代码改动。
- 状态：仅本地提交；未推送、未建 PR、未合并、未正式提交；非实现者验收仍待人工。
