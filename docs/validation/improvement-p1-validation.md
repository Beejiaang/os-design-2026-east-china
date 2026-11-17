# P1 改进目标机验证

日期2026-11-17，普通用户在原openEuler 24.03 LTS-SP4 / Python3.11.6执行。由同一代理验证，不是非实现者复现。起点44dbddd；未更改GPU功率、系统资源或安全配置。

## 各代码任务分别复验

新建 ~/projects/osdesign-p1-20261117 与独立venv ~/projects/osdesign-p1-venv-20261117。通过bundle获取源码；按下表逐个干净checkout。每个提交分别安装 `.[dev]`，运行pip check、Ruff、全量测试、默认完整pipeline和schema检查；不是只在最终版本上通过后追认之前提交。

| 任务 | 固定提交 | 全量测试 | 默认完整流程 |
|---|---|---:|---|
| 17 Ruff | f96e456 | 29通过、0跳过 | 18次最终化、15测量、3预热 |
| 18 extras | 5e0a9d9 | 29通过、0跳过 | 18次最终化、15测量、3预热 |
| 11负载证据 | 1bde76a | 32通过、0跳过 | 18次最终化、15测量、3预热 |
| 13区间可视化 | 2d60a88 | 34通过、0跳过 | 18次最终化、15测量、3预热 |
| 14源码指纹 | 0be73a7 | 36通过、0跳过 | 18次最终化、15测量、3预热 |
| 10规模扫描 | bb288cb | 37通过、0跳过 | 18次最终化、15测量、3预热 |

每轮独立analyze()核对完整性、stdout哈希及SQLite正确性证据，结束时osdesign-*单元为零、工作树干净。以上108次默认执行属于六个源码验证场景，不合并成同一历史性能基线。最初五轮在[分提交归档](../../evidence/improvement/p1-staged-openeuler-20261117.tar.gz)，最终轮及规模数据在[最终归档](../../evidence/improvement/p1-final-openeuler-20261117.tar.gz)，均见[SHA256SUMS](../../evidence/improvement/SHA256SUMS)。

普通用户离线开发依赖安装使用原有本地wheels目录，另下载并转入官方PyPI的Ruff0.17.5 Linux wheel，不在Git归档内保存第三方二进制；实际安装日志和pip freeze在分提交归档。执行器仍只用标准库。复现用的[分提交命令](../../evidence/improvement/p1-staged-command.sh)、[最终及规模命令](../../evidence/improvement/p1-scale-command.sh)保留真实路径，不含凭据。等价核心命令：

```bash
python -m pip install -e '.[dev]'
python -m pip check
python -m ruff check src workloads experiments tests scripts
PYTHONPATH=src OSDESIGN_INTEGRATION=1 python -m unittest discover -s tests -v
python experiments/run_pipeline.py --output results/本轮新目录
python scripts/validate_contracts.py results/本轮新目录/experiment/runs.jsonl
```

最终bb288cb的单元测试新增8项（采样3、SVG2、指纹2、内存解析1），共37项。Windows3.12.14同一代码纯测试为28通过、9项集成门控跳过，Ruff/pip check及两个schema样例通过，见[本地日志](../../evidence/improvement/p1-windows-python312-tests.log)。GitHub在线CI仍未运行，不能替代Ubuntu两版矩阵验证。

## 采样、指纹与历史报告

task11/13/14/10的默认完整轮各保存6条host-load记录，起止时间顺序、真实loadavg和引用计数检查通过，未见读取/写入错误。采集的是Linux来宾环境，不是Windows物理宿主机；附加数据不参与兼容或阈值判定。独立核查源码和输出在最终归档work/p1-validation/task10/。

最终src-py-v2摘要为`ea8b6911f3d7ee893b240795defbe66b611b60e36a466c59e9a42d93d0e4d386`；同一源码按legacy拼接算法为`c1de567a0aa857173ef8acb2ae814f132be771db1deab0c8d49279caf6f49562`。摘要不同，每条最终默认样本的runner_sha256均等于新算法重算值。run1.1字段形状不变，算法版本及旧数据处置见[协议](../contracts/data-contract.md#源码指纹算法src-py-v2任务14)。旧归档不重写；新旧摘要不同则无法历史比较。

报告使用原有真实48次规则实验中的baseline、healthy-1、boundary-15重新分析渲染。范围分别约0.9997–1.0320、1.1594–1.1599；不伪造真实跨阈值样本，跨阈值分支由明确标注的单测夹具验证。完整离线HTML与提取同一原始section的Edge无头截图在[视觉证据目录入口](../../evidence/improvement/p1-visual/healthy-1.html)：[健康复测截图](../../evidence/improvement/p1-visual/healthy-1.png)、[边界样本截图](../../evidence/improvement/p1-visual/boundary-15.png)。已检查中文、标签、参考线和布局；区间很窄时显示近似圆点，精确值同时保留。该图不是置信区间，不改判定规则。

## 三种规模实测（任务10）

固定种子20261117、每档1000组；50万/200万/800万行 × null/100/50，各一次预热五次测量。预热先行，随后规模/配额按固定种子混排。54次全部success、配额和清理核验通过、每份stdout与SQLite独立参考一致、输入和负载哈希前后不变、可见父级限制一致；45条测量进入下表，9条预热排除。

```bash
python experiments/scale_sweep.py --output results/scale-sweep --time-binary ~/projects/comparison-tools/time-install/bin/time
```

GNU time1.10外层记录wall/user/system（0.01s分辨率），内层`-f %M`单独记录Python聚合进程的最大RSS；[GNU手册](https://www.gnu.org/software/time/manual/time.pdf)定义该指标为最大驻留集大小，Linux结果按KiB记录。wall/CPU包含内层GNU time的启动/等待开销，计时边界与runner worker不同，不能拿本表与旧runner秒数直接排速度。RSS不包括输入生成/SQLite参考或整机内存，不是内存限额实验。

| 行数 | 配额% | n | wall中位数s | CPU中位数s | RSS峰值中位数KiB | 五次最大峰值KiB |
|---:|---|---:|---:|---:|---:|---:|
| 500000 | None | 5 | 0.20 | 0.20 | 17364 | 17412 |
| 500000 | 100 | 5 | 0.20 | 0.20 | 17372 | 17408 |
| 500000 | 50 | 5 | 0.38 | 0.20 | 17408 | 17412 |
| 2000000 | None | 5 | 0.77 | 0.76 | 17404 | 17416 |
| 2000000 | 100 | 5 | 0.77 | 0.76 | 17408 | 17412 |
| 2000000 | 50 | 5 | 1.50 | 0.76 | 17404 | 17416 |
| 8000000 | None | 5 | 3.06 | 3.04 | 17404 | 17412 |
| 8000000 | 100 | 5 | 3.05 | 3.03 | 17396 | 17412 |
| 8000000 | 50 | 5 | 6.06 | 3.05 | 17404 | 17408 |

本环境观察到时间随行数近似按规模增长，RSS在固定1000组下基本同量级；不宣称普遍线性、跨机器可迁移、统计显著性或生产可靠性。大CSV未入归档，固定参数/种子/输入哈希和SQLite参考保留在每个规模的input.json/reference.json，可按生成器复建。每个trial保存argv、stdout/stderr、GNU time原文、服务快照和清理结果；独立核查脚本再次逐份检查54个输出与内存文件。

## 局限与交付状态

旧RC1 PDF/Word/PPT不重生成，不声称已包含P1。动态干扰记录有限，仍无法排除温度/频率/虚拟化影响。验证由代理执行，不代表队友验收、教学效果或赛事接收。本轮未推送、未建PR、未合并、未打tag、未代办人工或视频事项。
