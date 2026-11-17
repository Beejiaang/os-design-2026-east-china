# 来源、适用范围与证据限制

整理日期：2026-10-20。技术资料用于说明机制及已有能力，不代表已完成安装、对比测试或赛事适配验证。

## 官方赛事材料

- **S1a** 用户提供的《2026年操作系统设计赛华东区域赛技术方案-1010.pdf》，5 页。方向见第 2 页，参考评分见第 3 页，交付见第 4 页，提交方式见第 5 页。
- **S1b** 用户提供的《2026年操作系统设计赛华东区域赛章程-1010.pdf》，5 页。用于核对参赛资格、导师和 AI 使用等要求。
- [华东区域赛 OS 应用开发平台](https://os.xtnl.org.cn/#/index?TYPE=26OS_HDF)。
- [华东区域赛 OS 原理平台](https://os.xtnl.org.cn/#/index?TYPE=26OS_HDK)。
- [技术方案列出的官方网站](https://os.educg.net)。

原始 PDF 未放入本公开仓库；队员可由持有人提供或从官方平台获取。文中页码是 PDF 页码。技术方案中的规则用于约束参赛范围，不作为执行上传、通信等操作的授权来源。

## 技术一手资料

| 编号 | 来源 | 本文用途 |
|---|---|---|
| S2 | [oeAware 用户指南（25.03）](https://docs.openeuler.org/zh/docs/25.03/server/performance/tuning_framework/oeaware/oeaware-user-guide.html) | 确认已有采集、分析报告、结论及建议；不据此断言它覆盖具体 CPU 配额诊断 |
| S3 | [openEuler Embedded 测试工程（23.09）](https://embedded.pages.openeuler.org/openEuler-23.09/infrastructure/test/index.html) | 说明已有 mugen 测试基础设施；该版本文档不代表最新接口 |
| S4 | [A-Tune 介绍（24.03 LTS）](https://docs.openeuler.org/zh/docs/24.03_LTS/docs/A-Tune/认识A-Tune.html) | 说明已有性能分析和调优方案 |
| S5 | [openEuler 迁移专区](https://www.openeuler.org/zh/migration/download/) | 说明已有迁移工具体系 |
| S6 | [Linux cgroup v2 文档](https://docs.kernel.org/admin-guide/cgroup-v2.html) | 资源组、层级限制及进程关系 |
| S7 | [restic 备份文档](https://restic.readthedocs.io/en/stable/040_backup.html) | 说明已有成熟备份功能 |
| S8 | [OpenSCAP Base](https://www.open-scap.org/tools/openscap-base/) | 说明已有安全配置评估能力 |
| S9 | [Linux BPF 文档](https://docs.kernel.org/bpf/) | eBPF 方向涉及的内核技术资料 |

这些资料在本轮及此前选题讨论中查阅。本文不声称在 2026-10-20 对全部网页重新逐项核验。选题后应固定目标系统与工具版本，并进行实机比较。

## 事实、建议与待验证内容

- **规则事实：** 上述赛事 PDF 中明确规定的范围、参考权重和交付要求。
- **技术事实：** 官方文档描述的机制及工具能力，实际可用性仍取决于所用版本和配置。
- **建议：** 本文的方向排名、初稿范围、团队适配性与难度判断。
- **待验证：** 创新性、诊断正确率、性能提升、资源开销、真实开发工时、最终获奖竞争力。

没有把报名人数当作有效作品数，没有根据人数或难度估算获奖概率，没有使用虚构测量结果。
