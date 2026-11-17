# Tasklist P1 执行进度

本页保留P1完成时状态，后续P2已处理，见[P2进度](improvement-p2-progress.md)。

2026-11-17，用户授权“继续下一轮”。基于P0的44dbddd，先完成文档，再做依赖与代码，最后规模实验。10项均有独立命名分支与提交；分支按顺序串联，当前 **improve/10-scale-sweep** 包含全部P0/P1，未合并回main。下表的提交固定各项内容，后续证据归档及导航更新不改原测量源码。

| 任务 | 本地分支 | 交付提交 | 结果 |
|---|---|---|---|
| 12样本量依据 | improve/12-sampling-rationale | 0df6e0d | 完成；n=5与单次预热动机、时间成本及统计边界 |
| 15状态头 | improve/15-readme-status | be85834 | 完成；保留冻结快照，列最近实测和硬缺口 |
| 16术语表 | improve/16-glossary | b0aa997 | 完成；统一quota/null/计时与全部完成状态，入口集中链接 |
| 19冻结后规则 | improve/19-freeze-policy | 0e30e7f | 完成；12/06后必要代码修复须标记并重验归档 |
| 17 Ruff | improve/17-ruff | f96e456 | 完成；默认E4/E7/E9/F、120列配置，机械修正3项，接入CI |
| 18 extras复用 | improve/18-extras | 5e0a9d9 | 完成；dev引用report extra并增加Ruff，不增加执行器依赖 |
| 11负载采样 | improve/11-host-load | 1bde76a | 完成；5秒旁路采样及起止记录，失败明确保留，不参与判定 |
| 13区间条 | improve/13-range-visualization | 2d60a88 | 完成；参考线/精确数值/缺失提示，真实HTML和截图留证 |
| 14源码指纹 | improve/14-source-fingerprint | 0be73a7 | 完成；src全部.py、相对路径与字节长度分帧、算法版本src-py-v2 |
| 10规模扫描 | improve/10-scale-sweep | bb288cb（实现）、7cc4042（实测） | 完成；三种规模×三档×一次预热五测量，54次独立校验通过 |

[逐提交目标机验证及量化表](improvement-p1-validation.md)记录命令、日志、来源、失败边界和证据；[数据协议](../contracts/data-contract.md)说明旁路采样与指纹版本，[统一术语](../contracts/glossary.md)说明指标口径。所有任务对应handoff和AI记录已补；早期“待目标机验证”由本轮验证表的实际结果覆盖，不能反向修改原始源码状态。

## 验证范围

六个代码相关提交**分别**完成openEuler干净源码全量测试、pip check、Ruff及默认18次pipeline；测试数依次29/29/32/34/36/37，全部0跳过。默认流程总108次最终记录，各轮15条非预热通过独立正确性证据检查；不混合不同源码的性能基线。额外规模扫描54次（45测量、9预热）全部SQLite/配额/内存/清理通过。Windows3.12最终37项中28通过9集成跳过；GitHub在线CI未运行。

RSS使用GNU time记录聚合子进程峰值，wall/CPU包含内层timer开销；不是runner同一计时范围。/proc/loadavg来自执行Linux来宾，不能冒充Windows物理宿主机。新指纹会拒绝与legacy记录直接历史比较；旧数据保留原样，不能补写新哈希。范围条不是置信区间，默认15%判定规则未改。

## 交付与后续

本轮只在本地提交，未推送、未建PR、未合并、未打tag、未正式提交；main保留原状。旧RC1 PDF/Word/PPT尚未重生成，材料表记录当前各份字节与内容提交，不代表所有材料都已对应最新源码。人员交叉验收、视频和平台/团队事实仍待人工。

P2任务20（CHANGELOG与建议tag）未执行；任务21为可选且依赖体积迁移，本轮未迁移，按清单保持现有文件名。下一步优先人工复核本轮改动及旧材料更新范围；推送、PR、合并需用户另行授权。
