# B：实验方案与配置区

`python3 experiments/run_pipeline.py --output results/group-first` 自动生成可追溯版本/输入的配置，执行 A 的原始实验，核对功能输出并生成报告。完整输出放 results/，经筛选的共享证据放 evidence/。运行环境、参数、固定规则和局限见 [完整流程说明](../docs/implementation/pipeline.md)；实测见 [验证记录](../docs/validation/pipeline-validation.md)。

默认三档配额、每档一次预热和五次测量，种子同时控制输入与执行顺序。正常复测使用新输出目录；受控变慢加 `--passes 2`。两边样本互不重叠，历史比较要求相同输入及兼容环境。先固定规则再收集验收样本，不根据结果反向调阈值。默认两百万行试验用于流程和初步规则检查，不能证明样本代表生产场景。

配置格式见 [数据协议](../docs/contracts/data-contract.md) 和 [config schema](../schemas/config-1.0.schema.json)。不复制一份 runner，也不在这里手工维护另一套结果状态。

新增 `compare_tools.py`（GNU time+systemd-run 正常场景对照）与 `validate_regression.py`（预声明规则边界验证）。前者需指定本机 GNU time 绝对路径；后者固定 100% 配额、默认每场景 7 次测量。干净 Git、独立新输出目录和固定规则是前提。原生对照记录是 tool-comparison-v1，不冒充 run 1.1。方法及命令见 [对照说明](../docs/implementation/tool-comparison.md)，真实数据与局限见 [扩展验证](../docs/validation/comparison-validation.md)。
