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
