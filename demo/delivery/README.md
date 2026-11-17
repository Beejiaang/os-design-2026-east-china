# 同伴复验交付包

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
