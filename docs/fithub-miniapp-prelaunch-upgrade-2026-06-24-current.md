# FitHub 小程序上架前大升级清单（当前版）

生成日期：2026-06-24

## 0. 当前结论

`https://fithub-cn.pages.dev/` 现在可以继续测试，但它不是最终建议的国内稳定入口：前端在 Cloudflare Pages，后端和数据已经迁到腾讯云 CloudBase。正式试运行应把前端也迁到腾讯云，形成“腾讯云前端 + 腾讯云 API + CloudBase 数据”的同域生态。

当前可执行目标：

- 腾讯云试运行 Web 入口：`https://zhangxin-zhinan-d4fwtsmr9a834d58-1401297280.tcloudbaseapp.com/fithub/`
- 腾讯云 API：`https://fithub-api-274271-9-1401297280.sh.run.tcloudbase.com`
- 当前数据存储：CloudBase 数据库，`/api/storage/status?remote=1` 已显示 `loadedFrom=cloudbase` 且 `remoteWritable=true`

当前门禁状态（2026-06-24）：

- `npm run check:trial` 已通过：腾讯云固定试运行入口、CloudBase API、持久化与核心功能库存可继续给测试用户使用。
- `python3 scripts/deploy_smoke.py --frontend-url 腾讯云/fithub/ --backend-url 腾讯云API` 已通过：前端壳、运行时 API 配置、后端健康、远端存储和 bootstrap 均可用。
- `npm run check:prelaunch` 仍然阻止正式提审：当前小程序仍是 `touristappid`，尚未配置微信合法域名、COS/CDN 媒体下载域名和备案后的 Web/API/Media 自定义域名。
- `npm run plan:tencent-launch -- --config deploy/tencent-cloud/launch-plan.json` 会生成正式上线执行计划，并列出微信公众平台后台需要配置的 request/uploadFile/downloadFile 合法域名和发布前人工核对项。
- 当前判断：可以继续用腾讯云试运行入口做真实测试；不要提交微信小程序审核，也不要作为正式公开运营入口。

长期上架目标：

- 自定义备案域名：例如 `https://app.你的域名/` 和 `https://api.你的域名/`
- 微信公众平台配置合法域名：request、uploadFile、downloadFile
- 媒体文件迁到腾讯云 COS/CDN

## 1. 今天必须完成的 P0 升级

### P0-1. 前端入口迁到腾讯云

目标：

- 不再把 Cloudflare Pages 作为正式国内试运行入口。
- FitHub 挂到 CloudBase 静态托管 `fithub/` 子路径，不覆盖已有项目。
- 每次升级都用同一个腾讯云入口。

验收：

- 腾讯云 `/fithub/` 页面返回 200。
- `/fithub/config.js` 指向腾讯云 API。
- 首页、探索、预约、我的四个页面能打开。
- Service Worker 更新后不会卡旧版本。

执行：

```bash
npm run deploy:tencent-static
npm run check:trial
python3 scripts/deploy_smoke.py \
  --frontend-url https://zhangxin-zhinan-d4fwtsmr9a834d58-1401297280.tcloudbaseapp.com/fithub/ \
  --backend-url https://fithub-api-274271-9-1401297280.sh.run.tcloudbase.com \
  --expect-frontend-api-origin https://fithub-api-274271-9-1401297280.sh.run.tcloudbase.com
```

说明：

- `npm run check:trial` 用来证明当前腾讯云固定试运行入口、CloudBase API、持久化和核心功能库存可继续给测试用户使用。
- `npm run check:prelaunch` 仍用于正式提审门禁，会继续阻止 `touristappid`、未配置 COS/CDN 或未备案正式域名进入审核包。

### P0-2. 后端和数据稳定门禁

目标：

- 每次发布后确认 CloudBase 数据仍然可读可写。
- 绝不允许回退到本地 JSON 或临时内存状态。

验收：

- `/healthz` 返回 200。
- `/api/storage/status?remote=1` 显示 `loadedFrom=cloudbase`。
- `remoteWritable=true`。
- 发布前后真实用户数、关注数、消息数不能异常归零。
- 生产快照会写入 `backups/`，并自动更新 `fithub-production-snapshots-manifest.json` 作为本地备份账本。
- 默认保留最近 30 天内快照，并始终保留最新 20 份，避免频繁升级时误删最近证据。

执行：

```bash
python3 scripts/production_write_acceptance.py \
  --backend-url https://fithub-api-274271-9-1401297280.sh.run.tcloudbase.com \
  --min-real-profiles 0
FITHUB_ADMIN_TOKEN=你的管理员token npm run snapshot:prod
```

### P0-3. 小程序正式配置检查

目标：

- 保持小程序代码可导入微信开发者工具。
- 当前先允许 `touristappid` 做开发调试；正式上架前必须替换真实 AppID。

验收：

- `npm run check:miniapp` 通过。
- 正式生产检查会阻止 `touristappid` 混进审核包。

执行：

```bash
npm run check:miniapp
cp deploy/tencent-cloud/launch-plan.example.json deploy/tencent-cloud/launch-plan.json
npm run plan:tencent-launch -- --config deploy/tencent-cloud/launch-plan.json
npm run check:wechat-domains
npm run check:prelaunch
```

说明：

- `plan:tencent-launch` 会把命令顺序、微信后台域名配置、COS/CDN 媒体域名和发布前人工核对项放在一份输出里，便于拿到企业主体和正式域名后逐项执行。
- `check:wechat-domains` 会输出 request/uploadFile/downloadFile 三类域名清单。
- 只要 AppID 还是 `touristappid`，`check:prelaunch` 必须失败，这是防止误提审。

待用户提供：

- 微信小程序真实 AppID。
- 微信小程序 AppSecret。
- 微信后台合法域名配置权限。

## 2. 上架前必须完成的 P1 升级

### P1-1. 媒体系统生产化

当前风险：

- 后端状态显示媒体仍是 `inline`，不适合真实视频/图片增长。

目标：

- 图片、头像、视频全部走腾讯云 COS。
- 生成缩略图和视频封面。
- 限制图片/视频体积，失败时明确提示。
- 动态、收藏、消息中的媒体加载走 CDN。

验收：

- `media.storageProvider=cos`。
- 上传 1 张头像、2 张动态图片、1 个短视频均成功。
- 刷新页面和换设备后媒体不丢。
- 列表页优先加载缩略图，不卡首屏。

### P1-2. 账号与多身份隔离

目标：

- 一个手机号/微信账号可以拥有健身爱好者、教练、健身房多个身份。
- 每个身份像独立账户一样拥有自己的消息、预约、动态、关注和粉丝。
- 切换身份只切当前身份上下文，不覆盖其他身份数据。

验收：

- 同一手机号下两个身份互相切换后，各自消息不串。
- 教练收到的预约不出现在训练者身份里。
- 训练者关注列表、教练关注列表互相独立。
- 换设备登录后所有身份都能恢复。

### P1-3. 预约与排课

目标：

- 教练/健身房可以发布可预约时间。
- 训练者可以按可预约时间下单或预约。
- 教练/健身房端看到“别人给我的预约”。

验收：

- 教练发布 3 个时间段，训练者端可见。
- 训练者预约后，教练端预约页出现待确认。
- 取消/确认后双方状态同步。

### P1-4. 内容安全与审核后台

目标：

- 符合微信小程序审核和真实运营要求。

必须补齐：

- 用户协议、隐私政策、账号注销说明。
- 举报入口、拉黑入口。
- 文本内容安全检测。
- 图片/视频安全检测：已接入 `media.safety` 本地兜底审核与 `moderationQueue` 入队；正式提审前接微信/腾讯云媒体安全 provider。
- 简易运营后台或管理接口：已提供 `admin.html`、`/api/admin/moderation`、`/api/admin/profile/moderation` 和 `/api/admin/content/moderation`，可处理举报、待审核内容、注销申请，可限制/恢复风险账号，并可隐藏、下架归档或恢复风险动态。

## 3. 上架前 P2 优化

- 绑定备案自定义域名，避免长期依赖腾讯云默认域名。
- 统一 UI 状态：按钮点击即刻反馈，所有提交动作有 loading/成功/失败态；小程序探索页的推荐关注、点赞和收藏已改为即时反馈，并纳入 `check_miniprogram.py` 与 `check:prelaunch` 库存检查。
- 加生产监控：已接入 `/api/monitor/event`、`/api/admin/monitor`，覆盖慢接口、失败接口、前端错误、媒体上传失败率，并纳入 `check:prelaunch` / `check:trial` 门禁。
- 加发布门禁：每次上线自动跑 smoke、生产写入验收、小程序脚手架检查。
- 做数据备份：`plan:tencent-launch` 已输出每日生产快照 crontab，默认保留 30 天且至少保留最新 20 份。
- 加小程序真机回归清单：登录、发动态、上传媒体、关注、评论、私信、预约、打卡、切换身份。

## 4. 今天完成后的判断标准

今天结束前，如果以下项目通过，就可以认为“进入小程序上架前正式大升级阶段”：

- 腾讯云 `/fithub/` 入口可用。
- 腾讯云 API smoke 通过。
- CloudBase 生产写入验收通过。
- `npm run check:trial` 通过。
- 小程序开发检查通过。
- 新清单和部署脚本已提交到 GitHub。

未完成但不阻塞今天的项目：

- 真实小程序 AppID 和 AppSecret。
- 自定义备案域名。
- 腾讯 COS 媒体生产配置。
