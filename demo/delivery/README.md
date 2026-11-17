# 同伴复验交付包

## 当前候选交付 RC1

[设计与测试报告Word](设计与测试报告_RC1.docx)、[PDF](设计与测试报告_RC1.pdf)为七页正式技术稿，覆盖实现、功能/性能测试、同类工具和限制；[哈希与来源](release-manifest.json)、[冻结复验](../../docs/validation/release-validation.md)可追溯。PPT已完成代理原生PowerPoint逐页版式检查，人员验收与视频按用户要求排除。

`scripts/build_release.py --output work/候选包.zip --wheels work/wheels`从干净已提交源码构建新的候选ZIP，附Git历史bundle、源码快照、材料、证据、离线依赖及逐文件MANIFEST。它排除嵌套ZIP和未跟踪工作文件，核验包内所有字节；不代替赛事提交与人工验收。源代码运行逻辑对应2697479，冻结完整复验提交086aff7，此后只有材料与记录补充。

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
