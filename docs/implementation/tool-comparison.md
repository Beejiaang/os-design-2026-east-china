# 原生命令组合的实测对比

日期：2026-11-17。范围是本队固定数据任务与系统机制，测量版本/原始证据见 [扩展验证](../validation/comparison-validation.md)。这不是覆盖全部性能工具的排名，也不证明本队优于成熟基准框架。

## 比较对象与来源

- GNU time 1.10：记录命令的 wall、user、system 和退出状态。`%e`、`%U`、`%S` 的含义见 [GNU 官方计时说明](https://www.gnu.org/software/time/manual/html_node/Time-Resources.html)。当前构建的数值输出采用百分之一秒精度，不能把打印位数与本队单调时钟打印位数当作准确度排名。
- systemd-run 255：目标机发行版构建为 v255-61.oe2403sp4。用户临时服务、CPUQuota、CPUAccounting、wait/collect 由系统提供；参考 [systemd-run 官方说明](https://www.freedesktop.org/software/systemd/man/255/systemd-run.html)。实际选项以目标机帮助及实测为准。
- 本队：runner/collector + 固定输入聚合 + SQLite 独立校验 + 分析/报告。底层资源约束仍由同一个 systemd/cgroup 提供，不能把 CPUQuota 实现称为本队原创。

目标机原先没有 GNU time。通过 HTTPS 获取 [GNU 官方 1.10 源码](https://ftp.gnu.org/gnu/time/time-1.10.tar.xz)，未修改源码，使用普通用户在 `~/projects/comparison-tools` 编译及安装，不改变全局软件或系统资源配置。源码下载 SHA256 为 `706bf7b8444ca9eb9037e9eda18e1d0eb7c2327ae7d8c2ce3a4823c5f80c7b11`，未另外验证上游签名；来源记录和本次内容校验分别说明。GNU time 自报 GPLv3+，本仓库没有纳入其源码或二进制，仅调用本机工具。

## 公平条件与边界

`experiments/compare_tools.py` 生成一份固定 CSV，先用独立 SQLite 计算参考结果；然后将工具、null/100/50 配额的预热和测量打乱，顺序执行。两种流程使用相同 Python、聚合脚本、输入字节、用户管理器、工作目录、父级限制和确定性输出。每工具每配额 1 次预热、5 次测量，共 36 次；不并行运行两组负载。

原生命令组合是 systemd-run 启动 GNU time，再启动同一负载。`comparison_probe.py` 在 exec 前保存服务内控制快照；循环、独立正确性、快照核验和清理检查均由本队比较脚本补充，**不能把这部分说成 GNU time 自带功能**。本队 A 单独执行也不证明算法正确，必须通过 B 的独立校验。两边都在测量之后核对每份 stdout。

原生方案使用 systemd 的 wait/collect，结束后验证本队创建的唯一临时服务已卸载/组已清理。本队方案使用已有 A 的采集与清理。快照与清理核验复用本仓库的系统读数/清理函数，只控制本次 UUID 服务，不修改其他进程。

记录两类时间：

1. 工具内部 wall/CPU：GNU time 以被测命令为边界；本队 wall 还包括 worker 计时区间内快照、保存、文件打开、等待/回收与末次采样。两者精度和开销不同，不能从 wall 差值推断谁更快或把差值归因为某一个机制。
2. outer_seconds：比较脚本从调用各流程至其返回并完成清理检查的单调时钟耗时。它不含输入生成、SQLite 参考和报告，不等于用户运行全部工作流的总耗时；只作本次流程开销记录。

原生记录保留 GNU 输出、argv、快照、返回值和清理证据，使用独立 `tool-comparison-v1` 格式；不伪装成 run 1.1。A 产生的 run 1.1 单次结果另存，但本次比较不是完整 A experiment 目录，不能直接作为 C 的历史回归基线。

## 本次结果

每格均为 5 次非预热测量中位数，单位秒；两边所有输出、配额核验、父级约束一致性与清理检查通过。

| 流程 | 本地配额 | 内部 wall | 子进程 CPU | 调用至清理返回 outer |
|---|---|---:|---:|---:|
| 本队 | null | 1.5673 | 1.5360 | 1.6400 |
| GNU time + systemd-run | null | 1.5300 | 1.5300 | 1.5818 |
| 本队 | 100% | 1.5673 | 1.5451 | 1.6388 |
| GNU time + systemd-run | 100% | 1.5400 | 1.5300 | 1.5865 |
| 本队 | 50% | 3.1206 | 1.5451 | 3.1916 |
| GNU time + systemd-run | 50% | 3.0400 | 1.5300 | 3.0862 |

这说明本环境内两套流程对固定任务的量级与限额趋势观察相近。本队没有在本次记录中表现出更小的流程开销；它增加了采集与证据管理，也存在计时范围差异，不能将数字解读为算法优化/系统加速或普遍的额外开销上界。

## 能力与本队增量

| 能力 | GNU time 单独 | systemd-run 单独 | 本队完整流程 |
|---|---|---|---|
| 命令 wall/user/system 与退出值 | 可提供 | 可等待退出并显示启用的资源统计，口径不同 | 明确字段、单位和异常状态 |
| CPU 时间上限 | 不负责 | CPUQuota/cgroup 提供 | 调用系统接口并核验实际控制值 |
| 固定输入的独立算法正确性 | 不负责 | 不负责 | 本任务使用 SQLite 参考逐次核对 |
| 多档重复、预热、顺序 | 需外部编排 | 需外部编排 | 已集成；本次对照同样由本队脚本编排 |
| 最终记录、原始证据关联与整轮完整性 | 需自建约定 | 需自建约定 | run 1.1、run_id、状态和完整性门槛 |
| 兼容前提与探索性历史复核 | 需外部脚本/其他工具 | 需外部脚本/其他工具 | 已实现；不宣称显著性或诊断准确率 |
| 超时/后代终止能力 | 单独不提供本项目服务清理流程 | 服务生命周期已有这些能力 | 编排这些能力，追加所有权/结果/恢复证据 |

成熟工具加脚本也能构建类似流程。当前可举证的增量是固定场景下的整合、独立正确性绑定、保守前提、异常与追溯协议及可复验产物，不是发明计时、CPU 隔离或新的统计方法。hyperfine、lkp-tests、mugen 等未在本轮实测，不能把本表扩大到它们，也不能据此宣称独特性或竞赛创新评分。

## 复验入口

```bash
python3 experiments/compare_tools.py --output results/tools-new --time-binary /实际路径/time
python3 experiments/validate_regression.py --output results/regression-new
```

两者要求干净 Git，输出目录必须不存在；使用已准备的目标 Python 环境。原始 GNU 工具安装版本及 hash、完整参数/证据、失败/限制见扩展验证。原生对照仅完成正常任务性能/输出对照，未覆盖其异常、权限、超时或全部功能；不把“尚未测试”写成“不支持”。

## hyperfine 补充实测（任务 1，2026-11-17）

固定 [hyperfine 1.19.0 官方发布](https://github.com/sharkdp/hyperfine/releases/tag/v1.19.0)，Linux x86_64 musl 压缩包在 Windows 下载后转入目标机，以普通用户解压到 ~/projects/comparison-tools/hyperfine-1.19.0，不改全局软件。内容校验不等于上游签名验证；未独立验签，仓库仅保留版本/哈希和原始数据，不包含第三方二进制。

- 下载压缩包 SHA256：`825287143f397774093539ca2458854ab3735c0e8a1aaf075c22edce7d261556`
- 可执行文件 SHA256：`404d32c40c5a201e47393a80998cf9b67e8662bced8889ea86249cf577273ee2`

新增三种方法同批 54 次（每种三档，各一次预热五次测量），同一 400 万行 CSV、种子 20261117 与固定聚合源码，每份 stdout 用 SQLite 独立参考校验。前 36 次项目/原生命令按既有种子混排；hyperfine 保留自己的 --warmup 1 --runs 5 批次，三档顺序以固定种子打乱为 100/50/null。**hyperfine 在前 36 次之后分批执行，未与另两种逐次交错，存在时间顺序混杂**，不作速度排名。

hyperfine 使用 --shell=none 调用本队 Python 适配器，每次建立独立 systemd 用户服务、运行 GNU time 包裹的负载、保存快照并核验清理。hyperfine 导出的 times 是整个适配命令（Python 导入、服务创建、快照、GNU time、退出及清理）的时间；内部 wall/CPU 列仍来自 GNU time，不是 hyperfine 原生的逐次 CPU 时间。预热输出也独立保存；hyperfine JSON 本身只含五条正式计时。

| 方法/配额 | 内部 wall 中位数 s | 内部 CPU 中位数 s | 外部命令中位数 s |
|---|---:|---:|---:|
| project / None | 1.5673 | 1.5346 | 1.6326 |
| project / 100 | 1.5672 | 1.5347 | 1.6442 |
| project / 50 | 3.0714 | 1.5380 | 3.1468 |
| gnu-time-systemd / None | 1.5200 | 1.5200 | 1.5671 |
| gnu-time-systemd / 100 | 1.5300 | 1.5200 | 1.5777 |
| gnu-time-systemd / 50 | 3.0400 | 1.5200 | 3.0875 |
| hyperfine-systemd / None | 1.5400 | 1.5300 | 1.6096 |
| hyperfine-systemd / 100 | 1.5300 | 1.5200 | 1.6072 |
| hyperfine-systemd / 50 | 3.0600 | 1.5300 | 3.1288 |

| 对象 | 自带能力 | 本队适配补充 |
|---|---|---|
| GNU time 1.10 | 单命令 wall/user/system/退出值 | 配额服务、重复/混排、独立参考、快照及清理 |
| systemd 255 systemd-run | 用户服务、资源控制、生命周期 | 固定数据、功能校验、可追溯逐次实验 |
| hyperfine 1.19.0 | 预热、重复、外部命令计时与 JSON 导出 | 三档服务、每次输出保留、SQLite 校验、实际控制/清理核验 |
| 本项目 d8a331e | 执行采集、原始证据、功能校验、比较门槛、离线报告 | 以上第三方底层能力按来源披露，不认领为原创 |

本队 worker 计时包含快照等额外范围；GNU time 内部计时与 hyperfine 外部计时范围不同，外部差值不能解释为算法加速。命令、全部逐次记录与新一轮完整流程见[任务1验证](../validation/comparison-validation.md#hyperfine-新增目标机验证任务-1)。

术语统一入口：[资源、计时与完成状态](../contracts/glossary.md)。
