# B：实验方案与配置区

`python3 experiments/run_pipeline.py --output results/group-first` 自动生成可追溯版本/输入的配置，执行 A 的原始实验，核对功能输出并生成报告。完整输出放 results/，经筛选的共享证据放 evidence/。运行环境、参数、固定规则和局限见 [完整流程说明](../docs/implementation/pipeline.md)；实测见 [验证记录](../docs/validation/pipeline-validation.md)。

默认三档配额、每档一次预热和五次测量，种子同时控制输入与执行顺序。正常复测使用新输出目录；受控变慢加 `--passes 2`。两边样本互不重叠，历史比较要求相同输入及兼容环境。先固定规则再收集验收样本，不根据结果反向调阈值。默认两百万行试验用于流程和初步规则检查，不能证明样本代表生产场景。

配置格式见 [数据协议](../docs/contracts/data-contract.md) 和 [config schema](../schemas/config-1.0.schema.json)。不复制一份 runner，也不在这里手工维护另一套结果状态。
