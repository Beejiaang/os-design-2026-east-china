# 两个可执行教学实验

运行前按README准备Python 3.11以上及systemd/cgroup环境，执行doctor。每次使用新的输出目录，保留原始结果。以下流程对应已有代理实测方法；本文件未声称学生学习效果已验收。

## 实验一 固定数据下的CPU时间上限

```bash
python3 experiments/run_pipeline.py --output results/lesson-quota
```

流程使用固定种子200万行输入、同一单进程聚合、null/100/50三档配额，每档一次预热五次测量。检查input.json、reference.json、experiment/correctness.json和各次result.json，随后对照report.html中的wall与CPU中位数及逐次点图。只看退出码不足以证明算法正确，必须核对SQLite独立参考。

解释任务：100%表示一个逻辑CPU的时间上限，null仍受父级限制；读取实际控制值和父级指纹，再解释为何wall可能变长而CPU时间量级接近。精确倍增不作通过标准。输入生成、参考计算与报告均不属于负载计时；缓存、启动开销和宿主机抖动仍会影响观察。已有目标机数值见pipeline-validation，不把本次新输出替换旧基线。

### 预期观察

[200 万行 openEuler 基线](../validation/pipeline-validation.md)中，null/100% 的 wall 中位数均为 0.8158s，50% 为 1.5175s，CPU 中位数为 0.7656–0.7681s。它们只提供量级参照，**以实际输出为准**；新机器不能混入旧性能基线。核对每档五条测量和单列预热，以及各次 SQLite 校验。

### 思考题

1. 为什么 CPU 时间量级接近，wall 却增加？哪项证据支持配额确实生效？
2. 为什么 100% 配额不是整机 100%？null 能否保证没有祖先或宿主机限制？
3. 为什么单次预热单列排除？一次预热是否保证缓存已稳定？
4. 退出 0 和 stdout 哈希一致分别能说明什么，为什么还要 SQLite 校验？

## 实验二 功能相同的受控变慢与兼容门槛

```bash
python3 experiments/run_pipeline.py --output results/lesson-base
python3 experiments/run_pipeline.py --output results/lesson-healthy
python3 experiments/run_pipeline.py --output results/lesson-slow --passes 2
PYTHONPATH=src python3 -m report results/lesson-healthy/experiment --baseline results/lesson-base/experiment --output results/lesson-healthy/history.html
PYTHONPATH=src python3 -m report results/lesson-slow/experiment --baseline results/lesson-base/experiment --output results/lesson-slow/history.html
```

三轮输入一致且每份输出须通过独立校验。passes=2实际重复完整处理、输出仍相同，版本标识记录参数变化。先核对资源/环境/输出的兼容理由，再读每档至少五条不同样本的中位数比。比值超过预设1.15给出slowdown_needs_review，不能直接说根因或统计显著；没有信号也不是“无退化”。

解释任务：比较配置实验与同配额历史比较的区别，指出预热为何排除。若输入、环境、正确性或完整性不满足，应返回unable_to_compare；不要修改原始记录强行通过。负向拒绝场景的明确单测/派生检查见comparison-validation，原始实测与派生夹具分别说明。

### 预期观察

[已有历史比较](../validation/pipeline-validation.md#历史复核规则检查)中，健康复测三档 wall 中位数比约 0.9999–1.0001；--passes 2 为 1.9213–2.0565，三档均提示 slowdown_needs_review。数值不是验收硬门槛，**以实际输出为准**；先查兼容理由和每侧样本数。不满足比较前提时，应保留 unable_to_compare。

### 思考题

1. 为什么 passes=2 的正确输出相同，却允许 workload_version 不同？
2. 不同配额的配置对照与同配额历史比较，各自固定了什么条件？
3. 比值恰好 1.15 与略大于 1.15 如何判定？没有信号能否说明没有退化？
4. 为什么观察范围跨阈值值得复核，但不能称为置信区间？
5. 改变输入或环境导致无法比较时，如何保留证据并设计下一次实验？

## 学生实验报告模板（一页以内）

- 环境：日期、操作者、源码提交及 dirty 状态、系统/内核/Python、CPU、实际 cpu.max 与可见父级限制
- 命令：安装、doctor、实验与报告命令；输出目录和输入 SHA256；预热/重复次数与顺序
- 观察：每档有效样本数、wall/CPU 中位数、逐次分布、SQLite 结果；历史比较理由与信号
- 解释：用原始 run_id 与资源控制证据支持解释；区分变化、信号、显著性与根因
- 异常：失败/超时/缺指标/清理及排除原因，保存日志路径；描述后续检查，不修写原始数据

模板用于记录过程，尚未据此评估教学效果或学生实际完成情况。

### 现场核对内核节流

在[实测报告与缺证据练习](../validation/quota-evidence.md)中选一条 50% 样本，读出 run_id、CPU 时间、耗时与节流次数。然后找一条 100% 样本比较。解释为什么“字段缺失”“字段为零”和“本轮实际出现节流”需要三种不同的表述。
