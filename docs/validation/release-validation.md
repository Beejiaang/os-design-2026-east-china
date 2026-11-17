# 候选交付 RC1 验证记录

日期：2026-11-17。用户要求完成除人工验收与视频演示之外的事项。本轮只整理工程交付和必要复验，不修改runner、collector、负载和分析逻辑，历史测量提交保持不变。

## 材料核验

- 正式[设计与测试正文](../implementation/design-and-test-report.md)覆盖需求、架构、协议、实现、功能/性能测试、同类对照、贡献、许可与局限；可编辑DOCX和PDF在demo/delivery，七页。生成器scripts/build_design_report.py支持重建DOCX。
- 首先尝试技能render_docx.py，因Windows运行环境没有LibreOffice而失败，保留本地错误；未安装额外Office。改用已安装Word原生UI导出PDF、bundled Poppler渲染每页检查，修正标题继承装饰线与孤立末页后，七页均无截断、乱码、重叠或孤页。
- 十页PPT在原生PowerPoint打开，无修复提示，实际逐页检查图表、文字、表格和布局；关闭后SHA256仍为9951ee0c63aaefc542e3508d2c7231aa57f24b6a17eae1a38b3b10345213f515。此为代理版式检查，不是答辩人员验收或通知规格确认。
- DOCX、PDF、PPT的实际哈希见[材料清单](../../demo/delivery/release-manifest.json)。原始实测与分析来源分别记录，不重新标记为本轮测量。
- HTML数据、转义和追溯已有自动检查；浏览器file协议操作此前被自动审批拒绝，未通过其他途径绕过，浏览器视觉检查保持待核验。
- [依赖许可索引](../records/dependency-notices.md)从实际wheel提取，分发保留原包许可；GNU源码/二进制未随项目分发。原创代码和文档许可入口保持不变。
- [两个教学实验](../implementation/teaching-experiments.md)沿用已实测流程，解释控制变量、正确性和复核边界，不虚构教学成效。

## 冻结源码复验

实际冻结提交为086aff71451ffaa4bd15a967a61984e445c5a720。2026-11-17 17:15:46—17:16:22北京时间，在全新检出`/home/holo/projects/osdesign-release-20261117`及全新venv完成离线可编辑安装。系统仍为openEuler24.03 LTS-SP4、原内核与Python3.11，依赖冻结见归档。

实际执行：`pip install -e '.[report]'`（PIP_NO_INDEX=1与既有wheel目录）、`pip check`、`python -m runner doctor`、`PYTHONPATH=src OSDESIGN_INTEGRATION=1 python -m unittest discover -s tests -v`、`python experiments/run_pipeline.py --output results/release`及`python -m report results/release/experiment --output results/release/recomputed.html`。

29项测试全部通过，0跳过；默认200万行完整流程18次均成功，输出独立校验、实际配额和清理通过；15条非预热、3条预热排除。最终schema验证18条通过，完整性issues为空，各档五条可比，重算摘要与原汇总逐档一致。Git开始/结束均干净，所有记录保留冻结提交；结束时osdesign-*临时服务0个。

| 本轮配额 | 非预热数 | wall中位数秒 | CPU中位数秒 |
|---|---:|---:|---:|
| null | 5 | 0.815700438 | 0.773123 |
| 100% | 5 | 0.815819821 | 0.770032 |
| 50% | 5 | 1.517467352 | 0.775262 |

原始[归档](../../evidence/release/release-openeuler-20261117.tar.gz)SHA256为463450c186a88cb59e3ef3b04dafa40fc87613cc5977e345fa1b4ab36f920b86；[二次核对](../../evidence/release/audit.json)保留schema、输出哈希、计数和摘要证据。大CSV按固定参数/哈希复建，归档不含该文件；其余原始路径未重写。此后追加验证文档/包不修改运行代码，不将这18次重标到后续提交；本轮仍不是人工或第二台机器验收。

## 发布与外部条件

正常Git凭据已推送feat/a-release-preparation与正式稿086aff7。原A的[PR2](https://github.com/Beejiaang/os-design-2026-east-china/pull/2)按expected-head约束普通merge成功，main合并提交db557e73b39fe804894e63fefb5338aa6bf66d2c；原始分支与提交历史保留。完整候选集成PR与最终包另续记实际远端状态，不强推。

全链路已建[PR3](https://github.com/Beejiaang/os-design-2026-east-china/pull/3)，以该PR实际状态核验合并。候选ZIP固定30e6a31（运行逻辑与086aff7无差异），所有112个内容文件哈希通过，bundle实际新克隆干净，包SHA256与使用说明见[交付入口](../../demo/delivery/README.md)。本轮8个原始证据归档哈希与3个材料哈希通过，37份Markdown本地链接通过。对当前文件及ZIP/Office/证据归档进行凭据标记与敏感文件名检查，未发现匹配；这是有限模式检查，不声称证明不存在一切秘密。未纳入work、私钥、虚拟机或原始赛事PDF。

[平台准备](../project/platform-readiness.md)保存本赛道实际入口与公开时间依据。队名、真实成员/贡献、指导教师、报名审核与官方GitLab项目未提供；不能替这些事实勾选。人工交叉验收与正式视频按本轮范围排除。GitHub发布与候选包不能代替GitLab和赛事平台接收。
