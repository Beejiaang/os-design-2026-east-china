# 新环境安装与交接材料验证

日期：2026-11-17，Asia/Shanghai。由同一代理执行，仍不算非实现者或队友人工验收。人员操作入口见 [复验指南](peer-reproduction.md)，记录使用 [空白模板](peer-review-template.md)。

## 源码与隔离条件

- 固定源码：`57c865e3f7298b1ac84dd9efe2756abf7dbd443b`，包含最终诊断 25b7f32；本轮主要新增材料，没有改变 runner/collector、负载或分析实现。
- 在原 openEuler 虚拟机中独立检出至 `/home/holo/projects/osdesign-clean-install-20261117`，新建 `/home/holo/projects/osdesign-repro-venv-20261117`，没有使用原开发虚拟环境的 site-packages。
- 系统仍为 openEuler 24.03 LTS-SP4 / x86_64 / Python 3.11.6，systemd 用户服务及 CPU 控制器已由此前环境准备提供。此检查不验证全新操作系统的初始化、sudo 权限或其他电脑兼容性。
- 从匹配 CPython 3.11 / Linux x86_64 的 wheel 集合离线安装 jsonschema 及其依赖和构建依赖；源码可编辑安装使用 pyproject 的 report extra。没有将 Windows 主环境中的已安装包冒充目标依赖。

## 实际检查

在新检出和新 venv 中执行：

```bash
PIP_NO_INDEX=1 PIP_FIND_LINKS=/实际准备的匹配wheel目录 python -m pip install -e '.[report]'
OSDESIGN_INTEGRATION=1 python -m unittest discover -s tests -v
python experiments/run_pipeline.py --output results/reproduction-smoke --rows 10000 --groups 100 --repeats 1 --warmups 0
env -u PYTHONPATH /新venv/bin/osdesign doctor
python -m pip check
```

这里的实际解释器路径为上述新建 venv，wheel 目录为 `/home/holo/projects/repro-wheels-20261117`。安装过程与完整命令日志保存在归档中。`runner.__file__` 确认来自这份新源码的 src/runner，不是原工程或旧虚拟环境。

结果：

- 可编辑安装成功，项目命令入口可调用，doctor supported=true。
- **29 项测试通过，0 失败、0 跳过**。
- 小试三档各一次、没有预热，3 条最终 success，独立正确性/实际配额/清理核验通过；summary.complete=true、eligible=3、excluded=0。
- pip check 返回 No broken requirements found；Git 工作树保持干净。

小试只检查流程，不给出配额耗时规律或历史回归结论。新环境的完整 18 次默认实验仍由未来实际操作者按指南复验；没有用本次 3 条小试冒充该环节。

## 证据与材料对应

[安装与小试归档](../../evidence/reproduction/clean-install-20261117.tar.gz) 保存 install/tests/smoke/doctor、依赖、源码版本与完整小试结果；校验值见 [SHA256SUMS](../../evidence/reproduction/SHA256SUMS)。

本轮演示与交接材料：

- [答辩工作稿](../../demo/presentation/答辩初稿_20261117_v1.pptx)，10 页，备注附讲解要点与来源；原始实验仍使用各自版本，没有因材料更新而重标。
- [讲解与 20 个常见问题](../../demo/defense-notes.md)、非实现者复验指南和空白记录模板。
- [素材来源与生成提示词](../../demo/assets/README.md)。封面概念配图不作实验硬件照片或测量证据。

PPT 是当前事实对应的工作稿，未在原生 PowerPoint 应用中验收或确认最终答辩形式；正式视频录制/托管、人员贡献、非实现者复验和平台状态仍待完成。报告的浏览器视觉验收也没有因本次 PPT 材料检查而自动完成。
