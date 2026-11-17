# 应用开发赛道平台准备

核对日期：2026-11-17。公开页面核验由代理执行，不代表队伍账号已报名或提交。

- [OS 应用开发赛道实际入口](https://course.educg.net/pages/contest/contest.jsp?contestCID=0&contestID=fLzatL8sv4E&doVisit=true&my=false)，页面题名明确为2026华东区域赛操作系统应用开发，阶段显示10/15 09:17—12/24 23:59；通用“结束02/01”不能当作品延期。
- [赛道官网](https://os.xtnl.org.cn/#/index?TYPE=26OS_HDF)。最新通知及账号内字段仍需实际登录核对。未拿鸿蒙专项页面作为本赛道报名入口。
- 现有 GitHub 为开发协作仓库，正式 GitLab URL 未提供。不能猜测组委会 GitLab 地址或向未知服务器上传；取得确切项目地址与已有访问权限后，可用普通 push 同步下面的提交与保留历史。

## 已准备与缺失信息

| 项目 | 状态与所需事实 |
|---|---|
| 工程及过程历史 | 已有完整 Git 历史和候选打包脚本，见交接的实际远端状态 |
| 设计及功能性能比较 | [报告正文](../implementation/design-and-test-report.md)、demo/delivery 可编辑稿、原始 evidence |
| 赛道入口与时间依据 | 已核对公开页面；截至本次核对无账号内接收记录 |
| 队名、成员与真实分工 | 用户尚未提供确认信息；不从角色代号推定 |
| 指导教师与报名审核 | 用户尚未提供确认信息；不能代签或虚构 |
| 官方 GitLab 项目 | 待提供确切 URL 和已有访问权限；尚未同步/提交 |
| 人工验收与正式视频 | 用户本轮明确排除，保留后续待办 |

## 有确切 GitLab 项目后的同步步骤

先核验目标项目的归属、可见性和参赛要求，再检查远端历史。以下命令中的 URL 必须替换为实际已确认项目；不使用 --mirror、--force 或删除远端分支。

```bash
git remote add competition 实际已确认的GitLab项目URL
git fetch competition
git log --oneline --all --decorate -20
# 确认不会覆盖远端后，普通推送指定集成分支
git push competition feat/a-release-preparation
```

若平台要求 main，再按其真实工作流合并，不能强推覆盖已有主分支。提交清单记录最终 SHA、提交人、北京时间、入口与接收凭据；凭据或证件保留私下，不进公开工程。网页实际提交的完整字段包含未提供的团队与视频信息，当前无法完成接收核验。

## 仓库体积与大文件策略（2026-11-17，任务 7）

测量基于 `c65611aff4830316bb082c87122e0f3c172973b3`，普通用户实际执行 git count-objects -vH；tracked 文件以 git ls-files -z 枚举后累加 stat().st_size（等价逻辑字节数，不包括 .git、忽略的 results/work、文件系统簇开销；不是整个桌面目录体积）。

```text
count: 435
size: 33.08 MiB
in-pack: 48
packs: 1
size-pack: 40.42 KiB
prune-packable: 0
garbage: 0
size-garbage: 0 bytes
```

当前检出的受版本管理文件总计 **35,096,440 字节（33.47 MiB）**。本地对象库 loose+pack 的上面数字另计，不能与工作树混称仓库下载大小；clone 的传输压缩量以实际网络为准。

| 已跟踪材料 | 字节 |
|---|---:|
| `demo/delivery/peer-review-kit-20261117.zip` | 8,083,253 |
| `demo/delivery/候选交付_20261117_RC1.zip` | 20,478,059 |
| `demo/delivery/设计与测试报告_RC1.docx` | 46,640 |
| `demo/presentation/答辩初稿_20261117_v1.pptx` | 1,399,997 |
| `evidence/comparison/comparison-openeuler-20261117.tar.gz` | 722,520 |
| `evidence/comparison/improve01-openeuler-20261117.tar.gz` | 404,388 |
| `evidence/integration/bc-openeuler-20261117.tar.gz` | 573,915 |
| `evidence/integration/bc-wsl-20261117.tar.gz` | 619,144 |
| `evidence/member-a/openeuler-20261116.tar.gz` | 10,127 |
| `evidence/member-a/stage2-openeuler-20261116.tar.gz` | 11,108 |
| `evidence/member-a/stage3-openeuler-20261116.tar.gz` | 21,561 |
| `evidence/release/release-openeuler-20261117.tar.gz` | 190,729 |
| `evidence/reproduction/clean-install-20261117.tar.gz` | 50,516 |

现有受版本管理文件与 Git 对象分别均未达到 100 MB，本轮不迁移，也不更名交付材料。继续保留 SHA256SUMS；大 CSV、虚拟机、第三方二进制不入库。后续若体积超过 100 MB，再评估 LFS 或正式 release 附件；迁移历史和外链替换需单独决策，不破坏现有归档哈希链。新增实验后可用相同命令重测。

## GitLab 命名与描述草稿（任务 9）

依据原始《2026 年操作系统设计赛华东区域赛技术方案-1010》第四部分：项目名建议为“选题方向和自定义名称：XX-Y”，描述列出高校名称、队伍 ID、队伍名、选题方向、项目名称。这里只准备文案，不注册、创建、同步或提交。

候选名（均未定名）：`方向A-CPU资源约束实验`、`方向A-数据任务性能比较`、`方向A-配额与回归分析`。其中“方向A”沿用团队选题代号；平台若要求官方完整选题字段，应按登录后的真实选项替换，不能将建议名当成审核通过名。

描述模板：

```text
高校名称：____；队伍ID：____；队伍名：____；选题方向：OS应用开发-方向A；项目名称：____
```

填空由团队确认，未猜测真实姓名、队名或 ID。规则 PDF 保存在工作区规则文件目录，原件未改；本地 MarkItDown 缓存文本第 253–273 行已核对。后续平台字段变化以官方登录页为准，本草稿不是已创建项目或接收凭证。
