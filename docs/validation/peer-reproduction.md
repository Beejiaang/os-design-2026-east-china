# 当前工程包的复验入口

使用 2026-11-18 工程复验包时，以包根 README.txt 中的分支、提交和离线命令为准。在新目录依次完成克隆、安装、全量测试和三档实验，保留自己的输出。版本化的设计报告与 PPT 见下文 RC2 材料，新增技术实测见[跨会话比较](../validation/login-session.md)。

# 非实现者复验指南

日期：2026-11-17。基准源码快照为 `57c865e`，包含 25b7f32 的诊断实现。下面是给实际操作者的步骤，尚未代替任何队友执行或填写通过。当前新环境安装由同一代理实测，记录另见 [安装复验](reproduction-validation.md)。

## 1. 获得指定源码并记录版本

当前分支尚未推送。可由持有人提供本轮复验包，包内的 `project-57c865e.bundle` 保留 Git 历史。不要从缺少当前功能的旧 main 开始，也不要覆盖已有工作树。在新目录执行：

```bash
git clone --branch feat/b-comparison-validation /实际路径/project-57c865e.bundle osdesign-peer-review
cd osdesign-peer-review
git rev-parse --short=7 HEAD
git status --short
```

期望提交为 57c865e、工作树为空。若通过后续 PR/远端获得代码，应明确记录实际提交与差异，而不是伪造该版本号。演示 PPT 和指南属于另行整理的工作稿，原始测量源码仍按各验证记录说明。

## 2. 检查系统前提

使用 Python 3.11+、cgroup v2、systemd 用户管理器及 CPU 控制器的 Linux。目标验收环境是 openEuler；WSL 可以验证流程，但需要单独记录，不能将性能样本混入 openEuler 基线。Windows 原生环境不支持这套系统执行机制。

```bash
python3 --version
stat -fc %T /sys/fs/cgroup
systemctl --user is-system-running
```

遇到权限/服务管理器问题，保留错误并由环境负责人处理。不要为了让测试变绿随意更改主机、安全策略或其他服务。

## 3. 新建隔离环境并安装

在全新检出中执行；不要覆盖已有同名环境：

```bash
python3 -m venv .venv-review
source .venv-review/bin/activate
review_dir="work/peer-review-$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$review_dir"
git rev-parse HEAD > "$review_dir/commit.txt"
python -m pip install -e '.[report]' > "$review_dir/install.log" 2>&1
python -m pip check
python -m runner doctor
```

doctor 应为 supported=true。它只做预检，仍需每次运行内实际核验配额。失败时保留 install/doctor 日志，不填安装或环境通过。

复验包的 wheels 仅对应本次 Linux x86_64 / CPython 3.11 的依赖集合，不能当作所有平台通用包。在匹配环境中可用以下离线方式替代上述 pip install 命令，`/实际路径/wheels` 替换为包内目录：

```bash
PIP_NO_INDEX=1 PIP_FIND_LINKS=/实际路径/wheels python -m pip install -e '.[report]'
```

当前只验收从源码可编辑安装；未验收独立 wheel 分发。pip/venv 的基础可用性仍需由目标环境提供。

## 4. 执行测试，区分跳过与通过

```bash
set -o pipefail
OSDESIGN_INTEGRATION=1 python -m unittest discover -s tests -v 2>&1 | tee "$review_dir/tests.log"
```

该快照在已准备 openEuler 的代理复验结果为 29 项、0 跳过。操作者必须记录自己的实际结果；未设置集成变量或缺少系统条件导致跳过，不能照抄 29 项通过。测试失败时保留失败内容和环境，先定位问题再重跑必要检查。

## 5. 小规模完整流程

```bash
python experiments/run_pipeline.py --output "$review_dir/smoke" --rows 10000 --groups 100 --repeats 1 --warmups 0
```

这是三档各一次、不预热的小试。期望三条最终 success、cleanup_ok 和 quota_verified 为 true，summary.complete=true，eligible 为 3、excluded 为 0，各条独立功能校验通过。小试不满足历史比较的样本数门槛，也不能用于说明配额耗时规律。

打开生成的 report.html，选一个 run_id，核对：

- `experiment/<run_id>/result.json` 中的状态、单位、实际 cpu.max、visible_limits、清理证据
- `experiment/<run_id>/stdout.log` 与独立参考结果
- `experiment/correctness.json` 对该 run_id 的 ok 和 stdout_sha256
- `input.json` 的种子、规模、内容哈希，以及配置的 input_id/workload_version

能解释这些字段，才完成这一步的理解核对；命令退出 0 不能代替算法正确性或人员理解。

## 6. 完整重复实验与历史离线报告

准备时间充分时执行完整配置：

```bash
python experiments/run_pipeline.py --output "$review_dir/full"
```

默认三档，每档一次预热和五次测量，共 18 条最终记录。应区分 15 条非预热和 3 条预热。失败仍需保留，不删掉失败文件来凑计数。

也可解包历史证据，离线复算报告，不执行负载：

```bash
mkdir -p "$review_dir/archive"
tar -xzf evidence/comparison/comparison-openeuler-20261117.tar.gz -C "$review_dir/archive"
python -m report "$review_dir/archive/results/regression/boundary-15/experiment" --baseline "$review_dir/archive/results/regression/baseline/experiment" --output "$review_dir/history-offline.html"
```

明确这是历史数据，原始环境/提交保持原样，不能声称当前机器重测。解释 no_threshold_signal 不等于无退化，阈值敏感也不是置信区间。原生工具对照是独立格式，不直接输入上述 run 1.1 报告命令。

## 7. 保存真实复验记录

复制 [人员复验记录模板](peer-review-template.md)，由操作者填写实际操作、是否使用代理、问题和结论。公开前检查日志中的凭据与无关私人信息。跨机器性能数据分别保存，不合并进同一基线。

最终至少能回答：100% 与 null 分别是什么、退出 0 和正确性有何区别、wall/CPU 的口径、哪些数据不能比较、清理失败意味着什么，以及现有 15% 规则的局限。
