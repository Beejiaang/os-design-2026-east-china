# B：负载源码区

已实现：`dataset.py` 生成固定输入并通过 SQLite 独立计算参考结果；`group_aggregate.py` 为单进程整数分组 count/sum 负载。`--passes 2` 是输出一致的受控变慢变体。运行入口在 experiments/run_pipeline.py；生成数据和结果进入被忽略的 results/。详见 [实现与测量边界](../docs/implementation/pipeline.md)。

先读 [Agent 交接](../docs/handoff/agent-handoff.md) 和 [数据协议](../docs/contracts/data-contract.md)。`examples/cpu_probe.py` 是 A 的探针，不能当正式聚合负载。
