# Changelog

记录会影响使用、复现与交付的重要变化，采用[Keep a Changelog](https://keepachangelog.com/en/1.1.0/)的未发布区、日期和分类结构。本文按已有提交与实测记录回填，不将开发版本、候选标签或代理验证视为正式发布/赛事接收。pyproject.toml中的软件版本仍为0.1.0。

## [Unreleased]

以下为RC1之后的本地P0/P1改进，尚未合入main、未重新冻结，旧RC1二进制材料未重生成。

### Added

- hyperfine三档对照及逐次输出留存，新增54次工具对照（含9次预热）；固定样本的10%/15%/25%阈值矩阵，每格保留run_id，见[P0验证](docs/validation/improvement-p0-validation.md)和[对照验证](docs/validation/comparison-validation.md)。
- 50万/200万/800万行规模扫描，共54次（含9次预热），逐份SQLite正确性、配额、内存和清理核验，见[P1实测](docs/validation/improvement-p1-validation.md)。
- /proc/loadavg旁路采样、历史观察范围区间条、材料版本与SHA256自动表、纯单元/schema CI、Ruff及开发依赖入口。
- 评审导读、开发时间线、教学观察/思考题、样本量依据、统一术语、README状态头、冻结后变更规则，以及本变更日志。

### Changed

- 源码指纹算法升级为src-py-v2，覆盖src全部Python文件，使用相对路径和内容长度分帧；新旧摘要不同则拒绝历史比较，旧证据不改写。run1.1/config1.0字段形状保持不变，迁移边界见[数据协议](docs/contracts/data-contract.md)。
- dev复用report extra，并增加固定版本Ruff；执行器仍只用标准库。

验证边界：六个代码提交分别完成目标机复验，最终运行源码bb288cb通过37项测试、0跳过及18次默认流程；Windows3.12纯测试有9项系统门控跳过，GitHub在线矩阵未运行。区间条不是置信区间，默认15%判定规则未改。[P0进度](docs/validation/improvement-progress.md)、[P1进度](docs/validation/improvement-p1-progress.md)记录各项提交与限制。

## [0.1.0-rc.1](docs/validation/release-validation.md) - 2026-11-17

RC1候选里程碑：本地已有注释标签`v0.1.0-rc.1`指向集成提交`54ef9281905b5316010b5484d62795fb8fb092ab`；本次只读取核对，不创建或移动标签，也未查询其当前远端状态。标签不能证明人工验收或赛事接收。

### Added

- 固定输入的单进程分组聚合、SQLite独立参考校验、配置对照与兼容条件下的探索性历史信号、离线HTML报告和逐次追溯。
- GNU time + systemd-run正常场景对照36次、健康/额外工作量规则边界实验48次，预热明确排除。
- 七页设计与测试报告、十页PPT、固定源码候选ZIP与人员复验准备材料，见[RC1交付入口](demo/delivery/README.md)。

### Fixed

- 损坏元数据在分析时保留问题提示，避免异常数据被当作完整实验。
- GNU time空指标文件明确报错；敏感性诊断保留原规则输出，不把观察范围当统计置信区间。

冻结复验源码086aff7，归档/候选包快照30e6a31；目标openEuler29项测试0跳过、18次默认流程通过。软件、材料、证据和集成提交分别记录，不把54ef928标签重标为原始测量提交。人工复验、视频与平台事项仍待完成。

## [0.1.0](docs/validation/member-a-validation.md) - 2026-11-16（开发里程碑，未正式发布）

此节回填当时pyproject.toml的0.1.0开发基线（de34b8c及后续可靠性补强），**不是v0.1.0正式发行记录**；本次本地标签清单中没有v0.1.0。

### Added

- systemd用户临时服务与三档CPU配额、固定argv执行、wall/子进程CPU/cgroup指标、原始JSON/CSV与实际控制证据。
- 环境预检、比较前提接口、干净源码复验流程、输入和代码身份门槛。

### Fixed

- 无本地CPU控制器时结合父节点证据核验，不将缺失cpu.max伪造为无限制。
- 加强超时/后代清理、中断保存、执行器丢失后的显式recover及所有权检查；恢复记录保留aborted，不改为成功。

A轮最终17项目标机测试与12次正常实验通过，故障注入记录单列，不作为性能样本。该开发阶段尚未包含后来B/C完整数据任务验收，也没有人员交叉验收结论。
