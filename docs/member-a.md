# 成员 A：系统执行与采集交付

日期：2026-11-16。代码在 `src/runner`、`src/collector`；分工依据 [work-allocation.md](work-allocation.md)。

## 使用

目标环境：openEuler 24.03 LTS-SP4 x86_64、Python 3.11.6、systemd 用户管理器、cgroup v2 CPU 控制器。使用已有普通用户运行，不需在每次实验中执行 sudo。程序不修改系统启动参数、用户持久服务或其他进程的限制。

在项目根目录运行：

```bash
export PYTHONPATH="$PWD/src"
python3 -m runner doctor
python3 -m runner run examples/cpu.json --output results/cpu-first
OSDESIGN_INTEGRATION=1 python3 -m unittest discover -s tests -v
```

当前虚拟机建议将上面 `python3` 替换为 `~/projects/osdesign-venv/bin/python`。每次使用新的输出目录，避免覆盖以前实验。也可通过 `python3 -m pip install -e .` 安装命令 `osdesign`，但零依赖的上述运行方式已足够。

`doctor` 只做预检；真正运行时还会读取服务内的 `cpu.max` 核验配额。环境不支持时退出 2；完整实验全部成功退出 0；任务失败、超时、指标缺失或清理失败退出 1。无效配置退出 2。

## B 的接入方式

复制 `examples/cpu.json`，将 `command` 改为负载的参数数组，填写 `workload_version` 与 `input_id`，在项目根目录执行。命令不经过 shell；需要重定向或管道时由负载自己实现。`cwd` 可选，默认调用目录；相对输入路径相对于该目录。

`workload_version` 必须能追溯实际负载实现，`input_id` 应包含种子、规模及输入校验值；执行器记录这些值但不替 B 验证其真实性。`examples/cpu_probe.py` 只是 A 的确定性计算探针，不代替 B 的分组聚合负载与独立正确性校验。

`quotas` 默认 `[null,100,50]`。100% 是一个逻辑 CPU 的时间上限，50% 是半个；null 表示本工具没有设置本地配额，仍受祖先和宿主机限制。`repeats` 默认 3；`warmups` 默认 0；`order_seed` 默认 0，使用固定种子打乱顺序，预热统一先运行。失败样本也保留，清理失败时立即停止后续实验。

## C 的数据接口（当前 schema_version 1.1）

字段、状态和版本兼容的完整约定见 [数据协议](data-contract.md)；旧 1.0 归档保留原样。

实验目录含 `config.json`、`environment.json`、`runs.jsonl`、`runs.csv`；每个 run_id 子目录含任务规格、启动日志、标准输出/错误、开始快照、完整测量和最终 `result.json`。JSONL 每行对应一次运行，CSV 是便于读取的扁平子集；JSON 中 null 在 CSV 中为空单元格。指标缺失不填 0。

| 字段 | 含义与单位 |
|---|---|
| schema_version / run_id / source | 协议版本、唯一运行编号、真实运行固定 measured |
| timestamp_utc / order_index / warmup | UTC 时间、执行顺序、是否预热 |
| environment | 系统、内核、CPU、Python、亲和性、控制进程可见限制、机器标识哈希、保守环境指纹 |
| command / cwd / workload_version / input_id | 参数、工作目录、负载版本、输入标识 |
| git_commit / git_dirty / runner_sha256 | 实验目录 Git 版本、未提交状态、执行器与采集器代码哈希 |
| quota_percent / cpu_max / quota_verified | 请求配额、服务内实际限制、核验结果 |
| visible_limits / parent_subtree_control | 服务内叶节点与全部可见祖先限制、父节点控制器启用状态 |
| wall_seconds | 从启动负载到回收直接子进程的单调时钟耗时，秒 |
| cpu_seconds | 已回收子进程的 user+system CPU 时间，秒 |
| cpu_stat_before / after / delta | cgroup CPU 原始统计与差值；usage_usec、user_usec、system_usec、throttled_usec 单位微秒，nr_periods、nr_throttled 为计数；保留内核实际提供的键 |
| stdout_sha256 | 标准输出 SHA256；输出含运行时长等非确定内容时不适合直接做历史比较 |
| status / exit_code / error | success、failed、timeout、error、metrics_missing、cleanup_failed、interrupted、aborted；错误说明和实际退出码，未知用 null |
| cleanup_ok / cleanup_detail | 临时单元已卸载且 cgroup 已删除或为空的核验与原始证据 |
| artifacts | 相对于实验目录的 stdout、stderr 路径 |

仅 `status=success`、`cleanup_ok=true`、`warmup=false` 的样本可进入常规性能汇总。任务退出 0 不等于功能结果正确；请结合 B 的校验器。

```python
from runner.compatibility import check_compatibility
preconditions = check_compatibility(baseline_row, current_row)
# 先检查 compatible，再由 C 实现分布、阈值和回归分析
```

兼容检查拒绝失败、预热、模拟、缺失关键指标、不一致输入、配额、运行环境、服务实际父级限制、执行器版本及标准输出；还要求同版协议和干净、可识别的 Git 提交。负载版本允许不同，因为它是历史回归的比较对象。此接口只提供前提核验，不输出“性能退化/正常”结论。

也可直接检查两个单次运行的 `result.json`：

```bash
python3 -m runner check-compatibility baseline/result.json current/result.json
```

退出 0 表示比较前提通过，1 表示不兼容并输出具体原因，2 表示文件读取或 JSON 解析失败。显式要求 measured、success、非预热、清理和配额核验为布尔 true、退出码 0、有效有限指标、cgroup CPU 证据及完整父级限制；不接受用字符串或数字冒充状态。

## 从干净源码复验

提交当前改动后，在项目根目录运行：

```bash
PYTHON=~/projects/osdesign-venv/bin/python bash scripts/reproduce-member-a.sh
```

脚本从当前 HEAD 创建独立本地检出，保留 commit、环境、测试日志和新一轮三档实验，并检查该检出的源码未被运行修改。证据默认留在 `work/member-a-reproduction-*`，不覆盖已有目录。它验证干净源码可运行；仍由同一代理在同一机器执行，不能计作队友独立复现或另一台机器验证。

## 实现与测量边界

执行器为每次运行创建唯一的 systemd 用户临时服务，设置 CPUQuota、CPUAccounting、KillMode=control-group、停止期限和额外 RuntimeMaxSec 看门狗。服务中的 worker 先采集 cgroup 快照，再启动负载并等待，之后写原子 JSON；外部执行器读取结果，再停止服务并核验整个组的清理。worker 自身超时杀死负载进程组，systemd 随后清理仍在组内的后代，包括另建会话的子进程。原始测量在停止服务前采集，避免 cgroup 删除后丢失统计。

worker 测量后保持运行，直到被执行器回收或看门狗终止；该等待不计入记录指标。原 RemainAfterExit 方案无法保证 active/exited 状态的运行时限，因此已替换。SIGINT/SIGTERM 记录 interrupted；强制丢失执行器后使用 `python3 -m runner recover 实验目录`，核验后记录 aborted，禁止改成成功样本。具体退出码、所有权检查与局限见数据协议。

无配额时 systemd 可能不为叶节点启用 CPU 控制器，此时叶节点 `cpu.max` 不存在；程序同时读取父节点 `cgroup.subtree_control` 来核验“未设置本地配额”，不会把缺失文件伪造为 max，也不把父级约束忽略。

`wall_seconds` 包含启动和回收负载的开销；`cpu_seconds` 不包含 worker 自身，cgroup 差值包含采样间隔内的 worker 开销。超时情况下尚未回收的后代 CPU 可能不计入 wait 统计，以 cgroup 差值和明确的 timeout 状态保留证据。首版以单进程负载为目标，不给多进程 CPU 归属保证。

临时服务只继承 systemd 用户管理器环境及显式 PYTHONPATH，不保证继承调用终端的所有环境变量。需要固定的随机种子、语言和线程数应由负载/启动命令明确设置并纳入输入标识。日志写到磁盘，不设容量上限，应使用受控负载。

环境指纹是保守的兼容门槛，不能证明宿主机负载、温度、频率或虚拟化调度完全一致。相同输出哈希也不代替算法正确性校验。重启/虚拟 CPU 数或运行路径变化可能需要重新建立基线。资源限制测试不构成恶意代码安全沙箱；不保证清理主动向其他服务迁移的进程。未实现统计回归判定或自动诊断。

## 依据与贡献

本次实现为本仓库新增代码，采用 [MIT](../LICENSE-CODE)；已有文档继续使用原 CC BY-SA 4.0。没有复制第三方项目实现，使用 Python 标准库、已安装的 Linux cgroup/systemd 接口。

机制参考：[Linux cgroup v2 文档](https://docs.kernel.org/admin-guide/cgroup-v2.html)、[systemd 资源控制文档](https://www.freedesktop.org/software/systemd/man/latest/systemd.resource-control.html)。文档可能描述较新版本，实际验收以目标机测试结果为准。

实测记录见 [member-a-validation.md](member-a-validation.md)。B/C 模块及非实现者复现、C 报告与真实输出的一致性审核仍需在对应模块交付后完成。
