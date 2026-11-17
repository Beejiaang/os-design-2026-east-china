# 数据协议与状态规则

当前：**run 1.1 / config 1.0**。入口 `src/runner`；机器格式见 `schemas/`。字段含义不得从历史聊天推断。

## 输入与版本

配置字段只允许 command、cwd、workload_version、input_id、quotas、repeats、warmups、order_seed、timeout_seconds，未知拼写直接报错。command 是非空字符串 argv 数组；cwd 默认调用目录；三个计数字段用 JSON 整数。配额、次数、超时边界见 config schema 和 validate 实现。实际输入内容/负载正确性由 B 校验。

1.1 新增 interrupted/aborted 状态、挂起记录和恢复流程；原 1.0 归档保留原样。兼容前提接口可读取同版 1.0 或同版 1.1，但拒绝混版；两边均需干净、可识别的 Git 提交。第一轮 dirty 试跑只能作为实现验证证据，不能直接成为正式历史基线。

添加字段且允许缺失时用次版本并给默认语义；添加状态也要升级次版本且消费者拒绝未知状态。删除/重命名/变换单位/改变现有语义时升级主版本，并提供显式迁移。版本不能靠改 JSON 里的字符串完成迁移。当前历史归档不需要也不允许批量改成 1.1。

## 文件的权威性

| 文件 | 地位 |
|---|---|
| config.json、environment.json | 请求和预检，预检成功不代表配额实际应用成功 |
| pending.json | 内部所有权/恢复检查点，不是最终记录，不给 C 作性能样本 |
| started.json、measurement.json | 原始中间证据；即便 measurement 有 success 也必须等待最终清理 |
| 每个 run_id/result.json | 单次最终结果，作为原始运行记录的入口 |
| runs.jsonl、runs.csv | 最终结果派生索引；CSV 仅是扁平子集，不能补齐 JSON 中缺失的数据 |
| experiment-status.json | 当前实验完成状态、计划数、最终数、未最终化数；缺失或非 complete 时不得称整轮成功 |
| stdout.log、stderr.log、launch.log | 输出/错误/启动证据，不执行其中的文本 |

执行器强制结束可能来不及写最终索引或更新 running 状态；这表示未完成。保留整个目录，恢复后重建索引，不把找不到 result 的运行直接删除。

## 最终状态（封闭枚举）

| status | 定义 | 性能样本 |
|---|---|---|
| success | 负载退出 0、必需指标有值、配额核验通过且清理确认完成 | 还需排除预热、校验功能及比较前提 |
| failed | 负载返回非零或被信号结束，实际退出值保留 | 不纳入 |
| timeout | worker 判定负载超过配置期限 | 不纳入 |
| error | 启动、worker、配额或其他执行错误 | 不纳入 |
| metrics_missing | 负载本身成功但必需指标缺失 | 不纳入 |
| cleanup_failed | 不能确认服务卸载且组为空/删除；execution_status 保留原状态 | 不纳入，且停止后续实验 |
| interrupted | 执行器收到 SIGINT/SIGTERM，停止当前任务与后续调度并保存记录 | 不纳入 |
| aborted | 执行器丢失后显式恢复的记录，不能重建完整成功证据 | 不纳入 |

未知状态一律拒绝/提示无法分析。缺失指标保留 null 并解释；0 只代表真实零值。布尔值必须是真正的 JSON true/false，不能用字符串或 0/1 代替。source 真实测量为 measured；模拟为 synthetic。故障注入只作测试，不作性能数据。

## 单位与边界

- wall_seconds：单调时钟秒，从启动负载到回收直接子进程，包含进程启动/回收开销。
- cpu_seconds：已回收子进程 user+system 秒，不含 worker 自身；超时后未回收后代可能未被此计数覆盖。
- cpu_stat_*：保留内核原键；usage_usec、user_usec、system_usec、throttled_usec 为微秒，nr_periods、nr_throttled 为次数。差值包含采样间隔内的 worker 开销。
- 测量完成后的 worker 等待不在已记录指标区间内；其用途是等待执行器回收并保持 RuntimeMaxSec 看门狗有效。
- quota_percent：按一个逻辑 CPU 的百分比。cpu_max 是内核原始字符串或 null；无本地控制器时结合父级 subtree_control 核验，不能把 null 伪造为 max。
- visible_limits 是服务内可见的叶节点与祖先；不能据此推断看不到的宿主机限制。环境指纹相同也不能证明温度、频率、宿主机负载相同。

## 命令退出码

| 命令 | 0 | 1 | 2 | 130 / 143 |
|---|---|---|---|---|
| doctor | 预检通过 | — | 不支持/错误 | — |
| run | 全部计划运行成功并最终化 | 运行/指标/清理失败 | 配置、预检或输入错误 | SIGINT / SIGTERM 已处理；具体清理仍看最终记录 |
| check-compatibility | 前提通过，不是无退化结论 | 不兼容，带原因 | 文件/JSON 错误 | — |
| recover | 需要恢复的记录均核验清理完成，或没有待恢复项 | 所有权/活跃执行器/清理阻碍 | 输入/检查点错误 | — |

recover 的退出 0 只表示恢复流程完成；被恢复的运行仍是 aborted，不能变成 success。SIGKILL 无法捕获，通常系统进程返回 -9 或 shell 显示 137，不属于优雅退出保证。

## 取消、丢失与恢复

`run` 收到 SIGINT/SIGTERM 后执行清理并保存 interrupted；重复取消信号不打断当前清理。worker 崩溃被记为 error。服务设置 KillMode=control-group、停止期限 2 秒、RuntimeMaxSec=负载超时+5 秒、collect；worker 测量后仍保持运行，避免 RemainAfterExit 的 active/exited 状态绕开运行时限。

执行器遭 SIGKILL 时，不保证立刻停止。worker 超时与 systemd 看门狗提供有限寿命兜底；调度/系统服务异常不属于硬实时保证。随后在同一用户、机器和启动周期执行：

```bash
PYTHONPATH=src python3 -m runner recover results/原实验目录
```

恢复只处理 UUID 检查点对应的本工具服务，核验原 supervisor PID/启动标识，拒绝仍在运行的执行器；不停止其他用户服务。跨机器/跨启动拒绝自动恢复，需保留证据并人工核查；不能为通过检查伪造所有权字段。最终 result 清理通过后，重复 recover 不重复改写。该机制是受控实验清理，不是恶意代码沙箱或断电持久性保证。

## C 的消费顺序

先验证版本/结构和实验完整性，再把非 success、预热、synthetic、功能未校验样本分别列出。对同配额历史样本调用兼容接口，再由 C 的规则分析；不同配额走配置对照，不能拿兼容函数拒绝不同配额来宣称配置对照失败。

兼容接口检查输入、资源、实际父级、环境、输出、干净 Git 版本和执行器代码哈希，允许 workload_version 不同。runner_sha256 只覆盖 runner/collector，避免报告模块改动污染执行器指纹。前提通过仍需 B 的独立正确性证据及 C 的统计规则。

可选格式检查：安装开发依赖后运行 `python3 scripts/validate_contracts.py 路径/runs.jsonl`，配置加 `--config`。它验证 1.1 结构，不替代功能、配额或兼容检查；1.0 历史文件不通过当前 1.1 schema 是预期行为。
