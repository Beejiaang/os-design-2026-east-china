# Tasklist 改进进度（P0）

本页保留P0完成时的历史状态；后续P1已执行，见[P1进度](improvement-p1-progress.md)。

2026-11-17，按工作区 work/codex-tasklist-20261117.md 执行。起点 main / 54ef928，工作树干净；本轮先完成 P0。每任务独立命名分支与提交，分支按任务依赖串联继承前项，**没有合并回 main**；当前 improve/09-gitlab-copy 包含本轮全部改进。运行实现只扩展任务1的对照编排，未改 runner/collector/正式负载或默认判定规则。

| 任务 | 本地分支 | 交付提交 | 状态与验证 |
|---|---|---|---|
| 1 hyperfine 实测 | improve/01-hyperfine | d8a331e（实现）、4f8ca84（证据） | 完成；54次对照、18次默认完整流程、29项0跳过、pip check |
| 2 阈值矩阵 | improve/02-threshold-matrix | 6f6fb7d | 完成；既有48次记录、15格、逐格run_id，默认阈值不变 |
| 3 评审导读 | improve/03-reviewers-guide | 31f6f28 | 完成；三份必读材料与五类索引，本地链接通过 |
| 4 开发时间线 | improve/04-timeline | 1d54111 | 完成；Git日期、提交、证据与过程记录可追溯 |
| 5 教学实验 | improve/05-teaching-observations | 4ccef58 | 完成；引用实测、9道思考题及报告模板，原命令保留 |
| 6 最小CI | improve/06-ci | c65611a | 完成配置与手动等价验证；GitHub实际未运行，详见下文限制 |
| 7 仓库体积 | improve/07-repository-size | 1e1a83f | 完成；真实字节与对象库测量，未达100MB，不迁移 |
| 8 材料版本清单 | improve/08-material-manifest | a4f4c04（脚本）、29b660f（验证） | 完成；可重跑、拒绝冻结材料漂移，第二轮目标机全量验证通过 |
| 9 GitLab文案 | improve/09-gitlab-copy | c5ec6a7 | 完成草稿；按原技术方案核对，真实团队信息留空 |

任务2在目标机未启动时先完成；用户启动虚拟机后回到任务1，其余按顺序推进。分支采用tasklist指定 improve/ 编号，优先于旧 AGENTS 的 feat/docs 命名建议；未推送、未建PR、未打tag、未改写历史。

## 验证证据

- [hyperfine及54次对照](comparison-validation.md#hyperfine-新增目标机验证任务-1)：源码d8a331e；45条非预热工具测量、9条预热，SQLite逐份正确性/资源/清理均通过；同时执行默认18次流程。
- [CI与材料脚本复验](improvement-p0-validation.md)：源码a4f4c04；第二轮openEuler 29项0跳过、18次默认流程及pip check。Python3.11纯测试与Windows3.12纯测试均20通过9跳过，两个schema样例通过。
- [材料对应表](material-versions.md)、[评审导读](../reviewers-guide.md)、[开发时间线](../history/timeline.md)、[体积与平台草稿](../project/platform-readiness.md)。冻结RC1 PDF/PPT字节与原哈希保持一致，新增数据未同步进旧二进制材料。

## 外部限制与后续顺序

CI仅手动执行等价命令：未推送，未在线运行GitHub Actions；Windows3.12不能冒充Ubuntu3.12矩阵验证。hyperfine按三档批次在前36次之后执行，有时间顺序混杂；只描述计时边界与证据，不排速度名次。15格矩阵为固定已有样本的事后阈值敏感性分析，不是独立统计准确率验收。

按tasklist，P0到此汇总，P1尚未执行。建议先做12/15/16/19的文档规则，再做17/18与CI依赖衔接，然后11/13/14的代码和协议改进，最后10的规模实验；有运行实现变化时需重新在目标机全量验证，不能沿用本轮源码的通过状态。任务14扩大指纹范围会使旧/新记录不再直接可比，实施前需说明版本语义及保留旧证据。

人工验收、视频、报名/导师/队伍事实、MIT咨询发送、正式GitLab与赛事提交均未代办。用户决定推送时应按当前串联分支范围统一审查，不能将最后一个分支误当作仅包含任务9。
