# 2026-11-18 配额节流证据与缺样本复核

## 评委可以现场核对什么

打开[本轮实测报告](../../evidence/improvement/quota-report.html)，先看配置对照，再任选一条 50% 测量，用 run_id 在归档的 results/review/experiment 中查同名目录。result.json 中的 cpu_stat_delta 与报告逐项对应，stdout.log 则可与该轮 SQLite 参考核验。学生可先预测限制 CPU 带宽对耗时和 CPU 时间的影响，再查内核计数解释两者为何不同。[内核 cpu.stat 文档](https://docs.kernel.org/admin-guide/cgroup-v2.html#cpu-interface-files)

| 第一轮配额 | 合格测量数 | 耗时中位数 s | CPU 中位数 s | 五次测量的节流次数 |
|---|---:|---:|---:|---|
| null | 5 | 0.8158 | 0.7715 | 全部缺少此字段 |
| 100% | 5 | 0.8159 | 0.7781 | 四次 0，一次 1 |
| 50% | 5 | 1.5676 | 0.7857 | 两次 15，三次 16 |

同一输入下，50% 档耗时约为 100% 档的 1.92 倍；CPU 时间中位数相差约 0.008 s。50% 档五条原始记录均出现服务节流。虚拟机调度、启动及采样也会影响耗时，单次记录无法把全部额外时间归因到某个机制。

## 对标与取舍

- hyperfine 提供预热、重复测量与导出。仓库既有的 54 次同机对照包含 GNU time + systemd-run、hyperfine 加本队适配器和本队流程，三者计时边界及执行顺序不同。本轮沿用固定输入、SQLite 独立校验和逐次证据，把内核实际节流计数放在耗时旁，供评委追问“这次真的发生过节流吗”。[工具实测与边界](../implementation/tool-comparison.md) · [hyperfine 上游](https://github.com/sharkdp/hyperfine)
- 2024 华东区域赛应用开发赛道二等奖 MyNote 在 OpenHarmony 上实现云同步笔记和限流；原理赛道二等奖《OpenEuler系统实验设计》将系统机制组织成十个实验模块。结合两个案例，本项目选一个可现场重做的任务，演示学生如何从耗时现象追到内核计数，以及证据不足时该如何作答。校方公开了作品和奖项，未公布逐项得分。[上海电力大学获奖报道](https://xxgk.shiep.edu.cn/f9/6f/c598a260463/page.htm)

本地《2026年操作系统设计赛华东区域赛技术方案-1010》第二节给出应用开发赛道参考权重。以下列出可检查的交付物。

| 评分项 | 本轮检查入口 |
|---|---|
| 代码 30% | 配置和历史对照保留零样本配额；缺测指标留空；测试覆盖缺失、布尔异常与真实零值 |
| 设计文档 30% | 上表给出实测结果、单位和计时边界；实现动机与同类工具的既有实测关联 |
| 有助于操作系统教学 10% | 学生可用三档实验区分 CPU 带宽上限、实际节流、进程 CPU 时间和耗时 |
| 工程规范 10% | 原始 run 1.1 字段及单位沿用；原始实验与派生缺证据夹具分别归档 |
| 演示与答辩 20% | 打开实测报告核对一条记录，再展示 50% 档样本为零时的历史比较。现场答辩与人员验收仍待团队开展 |

## 目标机复验

在 openEuler 24.03 LTS-SP4、内核 6.6.0-159.4.3.154.oe2403sp4.x86_64、Python 3.11.6 的独立干净检出执行。测量提交 5a5e109，父提交 f7dca19。设置 PYTHONPATH=src 后运行以下命令；最后两轮在同一 SSH 登录会话内依次执行。

~~~bash
python -m pip check
python -m ruff check src workloads experiments tests scripts
OSDESIGN_INTEGRATION=1 python -m unittest discover -s tests -v
python experiments/run_pipeline.py --output results/paired-a
python experiments/run_pipeline.py --output results/paired-b
python -m report results/paired-b/experiment --baseline results/paired-a/experiment --output results/paired-b/history.html
~~~

[复验归档](../../evidence/improvement/quota-evidence-1118.tar.gz)含测试日志、四轮原始记录及报告。大体积输入 CSV 可使用各轮 input.json 的种子与规模再生成并核验哈希。前两轮 review、repeat 来自不同 SSH 会话。两者功能校验通过，环境记录中登录 scope 名称及指纹不同，历史比较三档均返回无法比较。后两轮 paired-a、paired-b 使用同一登录会话。原来的兼容门槛继续生效。

在仓库根目录解开归档到新的空目录后，使用归档内脚本或[同一复验脚本](../../evidence/improvement/replay-missing-quota.py)，传入 paired-a/experiment、paired-b/experiment 的实际路径与新的 HTML 输出路径。脚本先复制两个实验到临时目录，仅从副本移除 50% 档正式运行的 stdout.log，检查该档保留为 0 对 0、无法比较、耗时比为空，另外两档仍有比值。归档中 work/review/derived.json 与 derived-missing.html 记录这次派生检查，临时路径仅供审计。

39 项目标机测试全部通过，跳过 0 项。四轮共 72 次，其中 60 次正式测量通过独立正确性校验，12 次预热单列。Ruff、pip check 通过，结束时工具服务列表为空。[打开缺少 50% 档输出的派生报告](../../evidence/improvement/derived-missing-50.html)。保留的 null、100% 档耗时比分别为 1.00009、0.99977。
