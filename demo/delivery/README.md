# RC3 工程复验版

[下载 RC3 离线工程包](工程复验_RC3.zip) · [SHA256 校验文件](工程复验_RC3.zip.sha256)

使用 2026-11-18 工程复验包时，以包根 README.txt 中的分支、提交和离线命令为准。在新目录依次完成克隆、安装、全量测试和三档实验，保留自己的输出。版本化的设计报告与 PPT 见下文 RC2 材料，新增技术实测见[跨会话比较](../../docs/validation/login-session.md)。

### RC3 解包实测

本地交付目录为项目工作区的 工程复验_20261118，ZIP 为 69,659,692 字节，内容清单 166 项。源码提交 9fc805006ea228e930e705319ff171709c770934，ZIP SHA256 为 ab7f0318041fcfe18deff5bf1663e8ac23b7618a97aa8babd6503fb0dde18135。在 openEuler 新目录解开实际 ZIP，从包根 README.txt 原样提取命令执行。新 Git 检出和新 venv 仅用包内 wheels 安装项目，pip check 和 doctor 通过，40 项测试零跳过，默认实验 18 次完成，其中 15 次正式样本进入分析、3 次预热单列，结束时工作树干净。[实际命令、日志、清单与原始数据](../../evidence/improvement/offline-rc3-verification.tar.gz)


# 当前候选材料 RC2

新材料：[9页报告Word](设计与测试报告_RC2.docx)、[PDF](设计与测试报告_RC2.pdf)、[12页可编辑PPT](../presentation/答辩材料_RC2.pptx)、[RC2独立清单](release-manifest-rc2.json)。本版纳入P0/P1/P2，原测量源码与材料版本分别记录，详见[材料核验](../../docs/validation/release-validation-rc2.md)。

RC2是候选材料名称，未打新tag、未人工验收、未含正式视频或赛事接收。旧RC1字节与清单保留；下方ZIP和旧复验包仍固定其历史快照。当前源码运行逻辑与已验证bb288cb一致，新的候选包构建后另记其精确源码提交，不能把旧ZIP当成最新源码。

# 同伴复验交付包

## RC2完整候选包

[候选交付ZIP](候选交付_20261117_RC2.zip)，43,825,302字节，固定干净源码`70580dc968edeba6e24cea14d240fdf45904d9a3`，157份内容文件加MANIFEST，含源码Git bundle与Linux x86_64 CPython3.11报告依赖wheels。包内Git bundle已新克隆，精确提交与干净状态通过；每份文件SHA256、RC1/RC2两个声明清单与图表9个实测值均核对通过。

SHA256：`eab420289e88867375f2c371ed9892d0903c4024566df4bbf51c18fb771cbab5`，另见[校验文件](候选交付_20261117_RC2.zip.sha256)。候选包源码的运行逻辑与bb288cb一致；打包后的仓库提交只补交付记录和ZIP，不重标测量提交。新包排除旧ZIP本身，Git bundle仍保留历史对象，不丢失开发过程。

只支持源码/可编辑安装与report extra离线依赖；dev extra的Ruff未放进此wheels集合，离线开发检查需另行准备。不能将该包当成正式视频、人员验收或赛事接收。旧RC1的包及材料继续保留在下文。

## 当前候选交付 RC1

[设计与测试报告Word](设计与测试报告_RC1.docx)、[PDF](设计与测试报告_RC1.pdf)为七页正式技术稿，覆盖实现、功能/性能测试、同类工具和限制；[哈希与来源](release-manifest.json)、[冻结复验](../../docs/validation/release-validation.md)可追溯。PPT已完成代理原生PowerPoint逐页版式检查，人员验收与视频按用户要求排除。

`scripts/build_release.py --output work/候选包.zip --wheels work/wheels`从干净已提交源码构建新的候选ZIP，附Git历史bundle、源码快照、材料、证据、离线依赖及逐文件MANIFEST。它排除嵌套ZIP和未跟踪工作文件，核验包内所有字节；不代替赛事提交与人工验收。源代码运行逻辑对应2697479，冻结完整复验提交086aff7，此后只有材料与记录补充。

实际[候选交付包](候选交付_20261117_RC1.zip)为20,478,059字节，源码快照30e6a311025600b78f10de98d3e2d5ae35e9173e，112个内容文件加MANIFEST。SHA256为41b626d51a834505a753896e5e699f617bef32476afa5bf55f1ff2de8acbd60b。包内Git bundle已实际克隆到新目录，提交与干净状态核对通过；所有包内文件逐个SHA256通过。源码快照与086aff7在src/workloads/experiments/schemas/tests/pyproject.toml无差异，未把材料更新冒充新一轮运行。

本ZIP固定上述内容，后续仓库提交补充打包与PR记录；不把ZIP自身递归纳入其源快照。完整集成入口为[PR3](https://github.com/Beejiaang/os-design-2026-east-china/pull/3)，是否已合并以PR实际状态为准，GitLab及赛事接收仍待确认。

## 较早的人员复验快照

`peer-review-kit-20261117.zip` 为当前人工复验准备的本地交付包，不代表已经发送给队友或完成验收。

包中包含：

- `project-57c865e.bundle`：固定源码快照及 Git 历史，使用指南中的显式分支命令克隆
- `wheels/`：本次 Linux x86_64 / CPython 3.11 的离线安装集合，其他平台/版本需另行准备
- `materials/`：当前十页答辩工作稿、讲解与常见问题、复验指南/模板、方法文档和公开证据归档
- `MANIFEST.json`：包内各文件 SHA256，解包后可核对

正式源码快照为 57c865e，材料是后续整理的工作稿，没有把材料提交号重标到原始测量。系统用户服务/CPU 控制器需由目标环境事先提供；包不配置系统权限、虚拟机或安全策略。

源目录中的 [答辩副本](../presentation/答辩初稿_20261117_v1.pptx) 与在线可编辑稿对应 stateVersion 3。图表的嵌入工作簿是本次完整实测数值的快照，不含虚构的来源 Excel 公式。后续在线修改应重新导出成新版本并更新 manifest，避免代码/材料错配。

开始前先读包内 `materials/docs/validation/peer-reproduction.md`。安装路径和操作者信息自行填写，未执行记录模板保持空白。正式视频、平台链接和非实现者验收仍未完成。
