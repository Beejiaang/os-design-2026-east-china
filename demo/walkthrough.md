# 完整流程演示脚本

日期：2026-11-17。这是可执行讲解提纲，尚非已生成视频。演示机器与提交必须在录制时说明，不能把 WSL 画面标成 openEuler。

1. 说明问题：同一个分组聚合任务，在固定输入与输出正确的前提下观察 CPU 配额和历史耗时变化。展示 Python、系统与 Git 版本。
2. 运行 `PYTHONPATH=src python3 -m runner doctor`，解释预检与每次实际配额核验不同。
3. 运行 `python3 experiments/run_pipeline.py --output results/demo-first`。解释固定种子、输入哈希、三档 null/100/50、预热和重复的含义。现场时间不足可展示完整历史原始结果，但明确不是当前实时执行。
4. 打开生成的 report.html。先看实验完整性和被排除预热，再看每档样本、中位数、逐次耗时点图与 CPU 时间。null 不代表整台机器无限资源，50% 不保证耗时精确翻倍。
5. 从报告选择一个 run_id，打开对应 result.json、stdout.log、correctness.json 和 input.json，核对单位、版本、输出哈希、SQLite 独立校验和清理证据。
6. 展示正常复测及 `--passes 2` 受控变慢结果。运行 `PYTHONPATH=src python3 -m report 当前目录/experiment --baseline 基线目录/experiment --output 当前目录/history.html`。说明前提不符为无法比较；超过预设 15% 仅提示复核，不代表统计显著或根因。
7. 展示 GNU time+systemd-run 对照表，说明底层能力来自系统/成熟工具，本队新增编排、独立校验与证据协议；计时边界不同，不按耗时表排名。展示额外 5/15/25% 边界样本，解释阈值敏感范围不是置信区间。
8. 结束前说明限制：非实现者复验、更广框架/波动验收、正式视频和赛事平台接收状态需单独核验。

录制前关闭无关窗口，避免显示凭据、私人聊天与报名资料。视频生成并实际托管后再填写 README 的真实链接。
