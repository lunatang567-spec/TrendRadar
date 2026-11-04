# TrendRadar 项目进度

更新时间：2026-11-04（北京时间）。**尚未正式上线。** 配置已实现，Cloudflare 账号、项目、Secrets 与发布验收尚待完成。

| 阶段 | 内容 | 状态 |
| -- | -- | -- |
| 1 | 检查原始仓库 | 完成：Fork 与上游同为 6.11.0、同一提交 |
| 2 | 修改新闻采集配置 | 完成：YAML 可解析，保留 11 平台，关闭 AI/通知/远程存储 |
| 3 | 配置关键词筛选 | 完成：官方解析器通过，37 个关键词组；真实采集匹配 52 条 |
| 4 | 配置每日自动运行 | 完成：Cron 与 workflow_dispatch 已检查，actionlint 通过；实际定时触发待验收 |
| 5 | 配置 HTML 网页生成 | 完成：真实生成 HTML，11 个完整热榜区，306 个新闻链接 |
| 6 | 配置 Cloudflare 自动部署 | 完成：工作流通过 actionlint；真实部署待用户配置与验收 |
| 7 | 运行自动化测试 | 本地部分通过；云端未运行：Actions 未登记工作流，validate.yml API 返回 404 |
| 8 | 创建 Cloudflare 项目和 Secrets | 待用户操作 |
| 9 | 首次真实采集测试 | 本地完成：11 平台全部成功，254 条新闻；GitHub 手动端到端运行待用户配置 |
| 10 | 新闻网站正式上线 | 待用户操作：完成首次部署和访问验收 |

## 已核对的仓库边界

- 唯一修改目标：`lunatang567-spec/TrendRadar`，默认分支 `master`。
- 初始 Fork 与上游 HEAD 均为 `946f52aa0704883f666c322888b8cd9af4cbcfff`，项目版本 `6.11.0`。
- `clean-crawler.yml` 原样保留。`crawler.yml` 的 Check Expiration 步骤与七天限制原样保留，无自动签到。
- 使用官方采集器、关键词解析器和 HTML 生成器，没有新增爬虫接口或重写展示程序。
- `index.html` 为不含历史新闻的静态占位页；正式首页只在采集时生成，不提交到 GitHub。
- 原仓库已跟踪 7 个 `output/news/2025-12-21.db` 至 `2025-12-27.db` 示例数据库；本次从当前分支移除它们，不改写旧 Git 提交历史。

## 用户下一步

先完成 [PR #1](https://github.com/lunatang567-spec/TrendRadar/pull/1) 的云端验证与代码审查，用户确认后再合并。随后按照 [部署指南](DEPLOYMENT_GUIDE.md) 第 1—5 节创建免费 Cloudflare Pages Direct Upload 项目，通过第 4.1 节的 API 设置 Production branch 为 `master`，在 GitHub 添加三个 Secrets。按第 6 节先运行 **Check In**、再运行 **Get Hot News**。成功后用电脑和手机检查完整热榜、关键词分类、新闻原文链接、生成时间及 Production 网址。

## 尚未验证

Cloudflare Token 的真实权限、项目归属、Production 分支配置、真实上传、域名访问、手机/电脑实机展示，以及次日 schedule 实际触发。不能把静态配置或本地报告测试视为网站上线。

## 实际测试记录

- YAML 解析通过；actionlint 1.7.7 检查 crawler、Check In 与新增验证工作流通过。
- 官方配置/关键词解析通过，37 组；AI 分析、翻译、通知、RSS、远程拉取关闭；本地存储启用。
- 现有测试与新增部署边界测试：排除 MCP stdio 集成模块时 30 项通过、35 个子测试通过。补齐官方直接依赖及部分锁定间接依赖后，全量测试 31 项通过，1 项 MCP stdio 握手在本机 Windows 隔离环境中超时；没有修改官方测试或 MCP 代码来规避。尚未在官方 Python 3.12 / uv.lock 完整环境验证。
- 新增测试覆盖：关键词为空仍显示完整热榜原文链接、只打包 HTML、旧首页无新报告时拒绝部署、空采集拒绝部署。
- 2026-11-04 11:20 北京时间真实采集：11/11 平台成功，254 条新闻，52 条关键词匹配；报告审计确认 11 个完整热榜分组和 306 个新闻链接（254 完整热榜 + 52 分类结果）。部分平台接口返回缓存，这是官方数据源行为。
- 发布目录审计通过，只含 index.html；数据库和历史目录不发布、不提交。真实采集使用本机 Python 3.14 隔离环境，GitHub 工作流使用官方 Python 3.12 和 uv.lock，需由新增 Validate news website 工作流继续核验。

## GitHub 提交与 PR 审查

用户已通过 Git Credential Manager 浏览器授权，原三个提交已推送。GitHub 插件写入仍受限，现使用本机 Git、gh 及内存中加载的 GCM 凭据；未将凭据写入仓库或日志。`gh auth status` 与 `/user` 已确认账号为 `lunatang567-spec`。gh 提示缺少 `read:org`，该范围不是本次个人仓库 PR/Actions 操作的必要条件，未扩大授权。

- PR：[Deploy TrendRadar daily news website #1](https://github.com/lunatang567-spec/TrendRadar/pull/1)，已创建，状态 OPEN、未合并。
- 合并方向：同一 Fork `lunatang567-spec/TrendRadar` 内，`codex/daily-news-pages → master`。GitHub 判断无合并冲突。
- 已 fetch origin，确认 master 仍为原始 `946f52a`；原开发分支为 `6540b7c`，三个原提交均存在。
- 原 19 个变更路径已审查，git diff --check 通过；新增行的已知密钥模式扫描为零，AI/远程存储凭据为空。核心 `trendradar/`、依赖文件与官方 Check In 无差异。
- Actions 权限 API 显示 `enabled: true`、`allowed_actions: all`，但工作流清单、运行记录和 PR checks 均为空。手动触发 validate.yml 返回 404（尚未在默认分支注册）。用户确认 Actions 页面只显示 “There are no workflow runs yet”。不能将其记为云端测试通过。
- 本次继续修正文档：Direct Upload 生产分支须通过 Cloudflare API 初始化，已提供隐藏输入 Token 的 PowerShell 步骤。不创建收费资源。

后续文档更新 `9dba0b7` 与工作流更新 `3e23746` 已在原开发分支正常提交并推送。工作流更新增加同分支去重，并把 actionlint 放在 Python 测试之前；未删除任何测试或降低标准。没有重复运行已通过的整套本地测试。

上述 push/PR synchronize 事件之后，Actions 运行列表、工作流列表和 PR checks 仍为空。通过 gh 重新保存原有 `enabled=true / allowed_actions=all` 设置成功，但单个 validate.yml 查询仍 404；默认 GITHUB_TOKEN 权限为 read，master 未启用分支保护。当前未能确定 GitHub 未登记工作流的根因，不能仅凭“没有失败检查”建议合并。

| 审查项 | 实际结果 |
| --- | --- |
| gh 登录身份 | 通过：lunatang567-spec，使用已有 GCM 登录 |
| origin / PR 方向 | 通过：自己的 Fork；codex/daily-news-pages → master |
| 初始工作区 | 干净，原三个提交均已推送 |
| 全部差异与敏感信息 | 已审查；未发现新增真实密钥；核心、锁文件、官方签到机制未变 |
| YAML、关键词校验 | 复用此前本地通过记录；云端未运行 |
| actionlint | 通过；最新工作流调整后再次检查通过；云端未运行 |
| Python 测试 | 复用本地 31 项通过、35 子测试通过、1 项 MCP stdio 超时；云端未运行 |
| 部署测试 | 复用本地三项通过；云端未运行 |
| 合并冲突 | GitHub 报告 MERGEABLE；不等于测试通过 |
| 合并结论 | **暂不建议合并，等待 Actions 能登记并完成全部验证** |
| Cloudflare | 命令、三个 Secrets 名称及 HTML 打包边界已核对；账户、项目、Token、生产分支初始化及真实部署待用户操作 |

当前 master 仍为 `946f52aa0704883f666c322888b8cd9af4cbcfff`，未合并、未直接修改 master、未强制推送。

## 2026-11-04 用户 OAuth 推送触发实验

- 独立提交 `9b13e4b44d7364c79da354b3d1d6001bc7025d5f`：仅在 validate.yml 添加一条中文注释，无功能变更。实验前工作区干净，本地与远程开发分支同步。
- 使用本机 Git Credential Manager 用户 OAuth 凭据，API 确认账号 lunatang567-spec；推送显式限定 manager 凭据助手，无 GITHUB_TOKEN、Git extraheader 或 askpass 覆盖。未保存任何凭据值。
- 推送开始：北京时间 14:23:41.089973；完成：14:23:45.723889（UTC 06:23:45.723889），exit code 0。远程分支、PR head 和工作流文件均核验存在。
- 推送前 Actions 已启用且允许 all；唯一变更路径 .github/workflows/validate.yml 匹配 push.paths，没有分支过滤或 skip-CI 标记。
- 至北京时间 14:27:30 的延时快照：gh run list 为空；gh pr checks 无检查；check-runs/status 均为零；工作流列表 HTTP 200、total_count=0。没有 run ID 或测试步骤日志。
- PR 作者为 OWNER，head/base 同仓库，审批策略为 first_time_contributors，未发现可见待审批运行；仓库非 archived/disabled。
- 不能追溯证明首次推送前的 Actions 启用状态，也不能仅凭 commit author 断言历史令牌类型。此前 9dba0b7、fcb5542 为纯文档推送，不匹配 push 路径过滤；3e23746 和本次实验均匹配。
- **纠正推断边界：validate.yml 不在 master 只能解释手动 workflow_dispatch 404，不能解释匹配的 push 未触发。** 本次用户凭据实验仍无运行，真正根因未确定；需 GitHub 排查内部事件处理、工作流登记或账户/仓库隐藏限制。
- 已保存推送前后 JSON、准确时间、权限与 API 请求 ID，并准备 Support 说明；未发送工单。云端 Python 3.12、uv sync、配置/关键词、actionlint、全部 Python 和部署测试均未运行。原本地测试结果不变，不宣称全部通过。
- 本次未更改 Actions 权限或 Cloudflare 设置，未合并 PR、未修改 master、未强推。

最终复查：工作区无数据库跟踪，七天签到工作流无差异；git diff --check、配置校验和 actionlint 通过。加强独立展示区的实际 HTML 节点检查后，三项新增部署测试再次通过。真实采集产生的本地 output 和部署目录已清除。
