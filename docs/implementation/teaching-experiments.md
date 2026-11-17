# 两个可执行教学实验

运行前按README准备Python 3.11以上及systemd/cgroup环境，执行doctor。每次使用新的输出目录，保留原始结果。以下流程对应已有代理实测方法；本文件未声称学生学习效果已验收。

## 实验一 固定数据下的CPU时间上限

```bash
python3 experiments/run_pipeline.py --output results/lesson-quota
```

流程使用固定种子200万行输入、同一单进程聚合、null/100/50三档配额，每档一次预热五次测量。检查input.json、reference.json、experiment/correctness.json和各次result.json，随后对照report.html中的wall与CPU中位数及逐次点图。只看退出码不足以证明算法正确，必须核对SQLite独立参考。

解释任务：100%表示一个逻辑CPU的时间上限，null仍受父级限制；读取实际控制值和父级指纹，再解释为何wall可能变长而CPU时间量级接近。精确倍增不作通过标准。输入生成、参考计算与报告均不属于负载计时；缓存、启动开销和宿主机抖动仍会影响观察。已有目标机数值见pipeline-validation，不把本次新输出替换旧基线。

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
