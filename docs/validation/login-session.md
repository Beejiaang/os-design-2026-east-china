# 重新登录后的历史比较

上轮在同一虚拟机上发现，基线和复测的启动进程分别位于 session-6.scope 和 session-8.scope，原比较器因环境指纹不同而拒绝三档比较。用户重新登录后重做同一实验，是工具日常使用中的一种合理场景。本轮保留原始环境记录，在判定时单独处理登录编号。规则和旧数据处理方式见[数据协议](../contracts/data-contract.md)。

## 复验方法

测量源码 ea91209，基于 d1a869b。目标系统 openEuler 24.03 LTS-SP4。在已安装项目依赖的环境从同一干净检出执行。两次登录分别设置 PYTHONPATH=src，使用同一 Python 解释器。第二次登录中的 taskset 仅改变本次启动命令及其直接继承进程的 CPU 亲和性；工作负载通过独立 systemd 用户服务运行。该对照用于检验工具能识别启动环境的变化。

~~~bash
# 第一次登录
python -m pip check
python -m ruff check src tests
OSDESIGN_INTEGRATION=1 python -m unittest discover -s tests -v
python experiments/run_pipeline.py --output results/base

# 退出并重新登录
python experiments/run_pipeline.py --output results/repeat
taskset -c 0 python experiments/run_pipeline.py --output results/changed
python -m report results/repeat/experiment --baseline results/base/experiment --output results/repeat/history.html
python -m report results/changed/experiment --baseline results/base/experiment --output results/changed/history.html
~~~

[目标机原始归档](../../evidence/improvement/session-compare-1118.tar.gz)包含三轮实验的逐次记录、两份历史比较 HTML、断言脚本、预期判定及实际输出。输入 CSV 可由各轮 input.json 重建。解包后使用归档内 work/check/check-session.py 依次传入三个实验根目录，可重新检查双向边界。

## 实测结果

40 项测试全部通过，跳过 0 项；Ruff 和 pip check 通过。三轮默认实验共 54 次，45 次正式样本均通过独立输出校验，另有 9 次预热。基线 session-21 和复测 session-24 均可使用 CPU 0 至 3。未设本地配额、50%、100% 的复测与基线耗时比分别为 1.00004、1.00000、1.00010。第三轮启动器亲和性变为仅 CPU 0，三档均返回 unable_to_compare，均无耗时比。

另用新报告工具离线读取上轮原始 review、repeat 目录，原先因登录编号被拒绝的三档均恢复到可比较，均未触发 15% 阈值。原始旧记录保留。以上是单台虚拟机和已记录控制条件下的验证。
