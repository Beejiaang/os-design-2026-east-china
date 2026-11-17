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

在本记录的下一次证据更新中填写实际冻结提交、目标环境、命令、测试和完整流水线结果；尚未执行的检查不写为通过。

## 发布与外部条件

正常Git凭据已推送feat/a-release-preparation初始快照2697479。完整候选稿后续普通push、PR和合并分别记录实际SHA。旧分支与提交历史保留，不强推。

[平台准备](../project/platform-readiness.md)保存本赛道实际入口与公开时间依据。队名、真实成员/贡献、指导教师、报名审核与官方GitLab项目未提供；不能替这些事实勾选。人工交叉验收与正式视频按本轮范围排除。GitHub发布与候选包不能代替GitLab和赛事平台接收。
