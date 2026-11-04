# TrendRadar 每日新闻网站部署指南

本 Fork 基于官方 6.11.0。北京时间每天 08:00 由 GitHub Actions 请求现有 11 个平台热榜；GitHub 的定时任务可能排队延迟，不能保证整点完成。官方七天签到有效期保留。网页同时显示关键词分类和完整热榜，条目数量以官方接口实际返回为准。

## 1. 创建 Cloudflare 账号

1. 打开 https://dash.cloudflare.com/sign-up ，填写邮箱和密码，点击注册，并完成邮件验证。
2. 登录 https://dash.cloudflare.com/ ，进入自己的账户。使用免费 Pages 静态托管即可，无需购买域名、AI API 或数据库，也无需开通 R2。

## 2. 创建 Pages 项目

1. 在左侧打开 **Workers & Pages**，点击 **Create application / Create**。
2. 选择 **Pages**（有些界面需要点底部 **Get started**），选择 **Upload assets / Drag and drop / 直接上传**。本方案使用 Direct Upload，由 GitHub Actions 构建，不要选择 Git 自动构建。
3. 输入项目名，例如 `trendradar-daily`。若被占用，换成自己的唯一名称；记下最终名称。
4. 在电脑新建一个 `index.html`，内容填 `<h1>TrendRadar 正在准备首次采集</h1>`，上传此文件或包含它的文件夹，点击 **Deploy site**。这是占位页，不代表新闻网站已验收上线。
5. 在项目 **Deployments** 查看 **Production** 部署。Direct Upload 项目没有控制台生产分支设置入口；创建 API Token 后，按第 4.1 节把生产分支明确设为 `master`，避免 Actions 的 `--branch=master` 只更新预览网址。
6. 记下控制台分配的正式地址，通常为 `https://项目名.pages.dev`。以控制台实际地址为准。

## 3. 获取 Account ID

在 **Workers & Pages** 概览右侧找到 **Account ID** 并复制；也可从 Dashboard 地址 `https://dash.cloudflare.com/<ACCOUNT_ID>/...` 取得账户段（通常是 32 位十六进制字符）。不要误用 Zone ID 或项目名。

## 4. 创建 API Token

1. 打开右上角头像 → **My Profile → API Tokens**，或账户 **Manage Account → Account API Tokens**。
2. 点击 **Create Token → Custom token / Create Custom Token → Get started**。
3. 名称填 `TrendRadar Pages Deploy`。
4. **Permissions** 添加 `Account → Cloudflare Pages → Edit`。
5. **Account Resources** 选择 `Include → Specific account → 你的账户`。
6. 无需配置 Zone 权限。点击 **Continue to summary → Create Token**，复制只显示一次的 Token，并妥善保存。不要贴到聊天、代码或日志。

### 4.1 设置 Direct Upload 生产分支（首次初始化）

本项目的发布命令明确使用 `--branch=master`，Cloudflare 项目的 `production_branch` 必须同为 `master`。Cloudflare 官方说明 Direct Upload 需通过 API 修改该设置，不能使用 Git 集成项目的控制台分支菜单。

完成前面账户、项目、Token 的创建后，在本机 PowerShell 逐段执行以下代码。提示时输入真实值；Token 使用隐藏输入，不会进入命令历史。该操作只更新现有 Pages 项目的生产分支，不创建收费资源。

```powershell
$cfAccountId = Read-Host 'Cloudflare Account ID'
$cfProjectName = Read-Host 'Pages 项目名称'
$cfTokenInput = Read-Host 'Cloudflare API Token' -AsSecureString
$cfToken = [System.Net.NetworkCredential]::new('', $cfTokenInput).Password
try {
    $cfProjectUri = "https://api.cloudflare.com/client/v4/accounts/$cfAccountId/pages/projects/$cfProjectName"
    $cfResult = Invoke-RestMethod -Method Patch -Uri $cfProjectUri `
        -Headers @{ Authorization = "Bearer $cfToken" } `
        -ContentType 'application/json' -Body '{"production_branch":"master"}'
    $cfResult.success
    $cfResult.result.production_branch
} finally {
    Remove-Variable cfToken, cfTokenInput -ErrorAction SilentlyContinue
}
```

期望输出 `True` 和 `master`。如出现权限错误，检查 Token 的 `Cloudflare Pages → Edit` 和指定账户范围。也可以先用官方 Wrangler 创建空 Direct Upload 项目：`npx wrangler login`，再执行 `npx wrangler pages project create 你的项目名 --production-branch master`；此方式需要本机安装 Node.js/npm，后续仍使用同样三个 GitHub Secrets。

## 5. 在 GitHub 添加三个 Secrets

1. 打开 https://github.com/lunatang567-spec/TrendRadar 。
2. 点击 **Settings → Secrets and variables → Actions → Secrets → New repository secret**。
3. 分别创建以下三项，名称必须完全一致；Value 中填写真实值，不要包含引号或前后空格。

| Name | Secret 值 |
| --- | --- |
| `CLOUDFLARE_API_TOKEN` | 上一步创建的 Token |
| `CLOUDFLARE_ACCOUNT_ID` | Cloudflare Account ID |
| `CLOUDFLARE_PROJECT_NAME` | Pages 项目名称，不填网址 |

不需要配置 AI、通知、R2 或 S3 Secrets。工作流不读取这些功能的凭据；缺少任何 Cloudflare Secret 会显示错误并停止部署，不能视为上线成功。

## 6. 第一次手动运行

1. 确认本次代码已在仓库 `master`。如交付的是 PR，先合并 PR。
2. 点击 **Actions**。Fork 若显示停用提示，点击 **I understand my workflows, go ahead and enable them**。
3. 左侧点击 **Check In → Run workflow → Branch: master → Run workflow**，等待签到成功。
4. 点击 **Get Hot News → Run workflow → Branch: master → Run workflow**。
5. 打开新运行 → **crawl**，依次检查 `Run crawler`、`Check Cloudflare config`、`Deploy to Cloudflare Pages` 成功。
6. 在 Cloudflare 项目 **Deployments → Production** 确认本次部署成功，打开正式网址。用手机和电脑检查生成时间、关键词分类、完整热榜以及新闻标题原文链接。
7. 若平台部分失败，官方会在报告和日志中提示。平台全失败或未生成新报告会阻止部署，不覆盖上一版可用网页。

PR 审查阶段先运行 **Validate news website**，不要先运行采集或发布。当前 PR 为 [#1](https://github.com/lunatang567-spec/TrendRadar/pull/1)，方向是同一 Fork 内 `codex/daily-news-pages → master`，需等检查通过且用户确认后再合并。

如果 Actions 没有任何工作流或运行记录，即使 **Settings → Actions → General** 允许 Actions，也不能视为测试通过。打开仓库 **Actions**，如出现 **I understand my workflows, go ahead and enable them**，点击启用；之后向开发分支推送必要更新以触发 PR 的 `synchronize` 事件。新增 `validate.yml` 尚未在默认分支注册时，直接手动触发可能返回 404，此时不要为注册它而提前合并业务 PR。

## 7. 每七天签到续期（必须手动）

每七天内至少操作一次，建议第六天操作：仓库 **Actions → Check In → Run workflow → master → Run workflow**。该官方流程删除工作流运行记录，以重置七天计时；本 Fork 未删除或绕过它，也没有自动签到。

如果已过期，`Get Hot News` 会被官方机制禁用：先运行 **Check In**；随后打开 **Get Hot News**，点击 **Enable workflow**（或右上角菜单启用），再 **Run workflow**。签到会删除运行日志，排错时请先查看/保存必要信息。

## 8. 检查每日更新及排错

- 每天 08:00 后打开 **Actions → Get Hot News**，确认最近一次事件是 `schedule`，并检查运行是否成功；GitHub 可能延迟触发。
- 网页生成时间应对应当天本次运行。刷新浏览器，并在 Cloudflare **Deployments** 检查 Production 最新时间，不能仅凭 Actions 绿色判断网页内容。
- 采集失败：打开 **crawl → Run crawler**，检查网络/API 错误、失败平台、域名校验告警和生成报告日志。使用原有接口，不要随意更换不明接口。
- 缺 Secrets：按第 5 节补齐全部三项后重跑。Token 无权限/失效：重建 Pages Edit Token 并更新 GitHub Secret。找不到项目：核对项目名称与 Account ID 是否属于同一账户。
- 部署到 Preview：按第 4.1 节通过 Cloudflare API 把 Production branch 设为 `master`。Direct Upload 没有控制台分支菜单；工作流明确使用 `--branch=master`。
- 超过七天：按第 7 节签到、重新启用并运行。
- Fork 长期无提交时 GitHub 还可能因仓库不活跃停用定时工作流；在 Actions 页面检查并启用。免费额度和服务规则以 GitHub/Cloudflare 当前页面为准。

## 9. 修改关键词与平台

编辑仓库 **config/frequency_words.txt → 铅笔图标**，在 `[WORD_GROUPS]` 后添加分类：第一行 `[分类名]`，下面每行一个关键词；同组为“或”，组之间空一行。保留官方格式说明。提交到 `master` 后，下次运行生效。

关键词只控制分类结果，完整热榜由 `config/config.yaml` 中 `display.standalone.platforms` 单独展示，`max_items: 0` 不裁剪。添加平台时应先验证官方接口并同时配置该列表。

## 10. 数据生命周期与部署边界

每次在全新 Actions Runner 本地使用临时 SQLite；不缓存、不上传 artifact、不提交任何新闻输出。发布目录只含最新 `index.html`，运行结束清除数据库和输出。仓库已有的示例首页不会被直接部署，必须由本次采集重新生成。

Cloudflare 本身会保留部署版本以支持回滚，本方案没有历史新闻入口，也不上传历史目录或数据库；它不是跨运行新闻数据库。若要求连托管商旧部署副本也删除，需在 Cloudflare 控制台删除旧部署。

参考官方说明（核对日期：2026-11-04）：[Direct Upload](https://developers.cloudflare.com/pages/get-started/direct-upload/)、[CI 部署与 Token 权限](https://developers.cloudflare.com/pages/how-to/use-direct-upload-with-continuous-integration/)。

## 11. 如代码尚未推送到 GitHub

本地仓库位于 `D:\MyMind\TrendRadar`，分支为 `codex/daily-news-pages`。代码已推送，且 [PR #1](https://github.com/lunatang567-spec/TrendRadar/pull/1) 已创建。后续必要修复仍可在此分支执行：

```powershell
cd D:\MyMind\TrendRadar
git push -u origin codex/daily-news-pages
```

已有 PR 会随推送更新，不要重复创建。确认 **base repository** 为 `lunatang567-spec/TrendRadar`、**base** 为 `master`、**compare** 为 `codex/daily-news-pages`，检查 **Validate news website**。测试通过并获得用户明确确认后才合并。不要运行 GitHub 上尚未合并改动的旧采集工作流。
