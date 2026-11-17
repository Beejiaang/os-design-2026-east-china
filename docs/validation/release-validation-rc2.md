# RC2候选材料核验

日期2026-11-17，基于7ef8f88，分支improve/22-current-materials。本轮角色A集成，按用户继续推进的授权同步报告、PPT和交付清单；不修改src、workloads、experiments、tests、schemas、pyproject或CI。原RC1文件、标签与声明哈希保留。

## 新候选材料

- [报告正文](../implementation/design-and-test-report-rc2.md)、[Word](../../demo/delivery/设计与测试报告_RC2.docx)、[PDF](../../demo/delivery/设计与测试报告_RC2.pdf)：9页，纳入37项测试、三类工具、阈值矩阵、规模/内存、旁路采样和src-py-v2边界。
- [十二页可编辑PPT](../../demo/presentation/答辩材料_RC2.pptx)：含3份原生表格、1份原生规模柱形图、真实观察范围截图及逐页来源备注。新建图表工作簿为完整实测值的字面快照，不是恢复了原有公式或来源工作簿。
- [独立RC2材料清单](../../demo/delivery/release-manifest-rc2.json)绑定四份文件，原release-manifest.json仍只绑定RC1。材料表生成器同时核对两个清单，发现声明冲突或字节漂移则报错，不自动改写旧清单。

RC2是本轮候选材料名称，没有创建新tag或宣称已正式发布。最新实际运行源码bb288cb仍对应37项0跳过、默认18次与54次规模扫描；工具对照仍标d8a331e，规则旧数据仍保留8d76aed/25b7f32。不同来源未合并成同一性能基线。

## 文档渲染与版式检查

使用bundled Python和python-docx生成。已运行技能render_docx.py，因bundled路径没有LibreOffice soffice.exe失败，错误日志保留。随后通过本机已安装Office的Word兼容COM接口导出PDF；PDF元数据Creator为WPS文字，不能将其记为原生Microsoft Word检查。导出成功后Quit曾返回RPC失败，最终PDF实际可解析、页数/文本/全部页面图像核对通过；没有据此忽略导出文件检查。

初稿末段形成第10页孤页，缩短索引表重复路径说明后重新导出为9页。bundled Poppler将最终PDF全部渲染为PNG并逐页检查；未见文字裁切、表格重叠、乱码或孤页。运行入口：

```bash
python scripts/build_design_report.py --source docs/implementation/design-and-test-report-rc2.md --output demo/delivery/设计与测试报告_RC2.docx --release-label RC2
```

旧脚本默认参数仍输出RC1；本轮使用显式参数，仅写RC2新文件。该作者工具不属于执行器运行依赖。

## 演示稿结构和视觉检查

使用Artifact Session创建并渲染12页，不复制旧PPT为新实测。修复首轮图片未嵌入及图表标签偏小问题，明确所有文本字体为Microsoft YaHei；最终逐页检查。PPTX经finalizer核验：12页、1个原生图表、指定第4/7/8页原生表格、图表9个缓存数值与嵌入工作簿对应、字体策略通过、结构及布局均0项问题。第一方导入最终PPTX成功。

finalizer仅为新字面数据图表补充可编辑工作簿，不声称保留了原公式。最终PPTX重新导入并逐页渲染，12页像素与已检查版本一致，未新增版式差异。PPT未在原生Microsoft PowerPoint打开，不能沿用旧RC1的原生检查结论；仍待人员实际展示和答辩验收。

作者脚本scripts/build_rc2_slides.mjs通过Artifact Session回调build(presentation)创建新空文稿；会话不含原生导出工具模块时使用文档化presentation.export接口。导出文件经file-authoring finalizer后归档，最终文件哈希以manifest为准，实时会话后续编辑不会自动改写固定交付PPTX。

[材料QA归档](../../evidence/improvement/rc2-material-qa-20261117.tar.gz)含9页报告PNG、12页最终PPT PNG、finalizer回执与转换/渲染辅助命令；校验值在[SHA256SUMS](../../evidence/improvement/SHA256SUMS)。PNG供技术追溯，不作为额外用户交付项。其检查是代理版式与结构核验，不等于人员验收。

## 运行源码与版本纪律

相对bb288cb的src/workloads/experiments/tests/schemas/pyproject与CI差异应为空；本轮仅改变作者/打包/材料表脚本及文档、材料、QA证据。Ruff通过，材料清单生成两次一致，错误哈希临时夹具被拒绝；不为纯材料变化重跑性能测试，不把新提交冒充旧实测。

旧RC1三个二进制声明哈希及原ZIP不变，已有evidence条目逐项校验。候选包构建以干净提交为准，源码与材料提交、原测量源码分别记录；新包不递归收集旧ZIP、工作缓存、凭据或虚拟机。

人工复验、正式视频、团队/导师/报名事实、GitHub在线CI和官方GitLab/赛事接收仍未补齐。未推送、未建PR、未合并、未创建/移动标签。
