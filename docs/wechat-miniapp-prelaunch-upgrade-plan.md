# FitHub 微信小程序上架前总体修复升级方案

生成日期：2026-06-23

## 1. 结论摘要

当前 FitHub 已经具备网页试运行和小程序 MVP 骨架，但还不适合直接提交微信小程序审核。主要原因不是单个页面问题，而是生产链路还没有达到“小程序可审核、可稳定使用、可持续运营”的标准。

本次审查结论：

- 当前网页前端 `https://fithub-cn.pages.dev/` 可访问，但它仍依赖 Render 后端 `https://fithub-app-1btg.onrender.com`。
- 本次线上 smoke 检查发现后端存储处于 `local-fallback` 降级状态，Supabase 远端不可写，`real_profiles` 显示为 `0`。这是 P0 问题，必须先修。
- 后端健康检查这次出现过约 25 秒返回，说明冷启动或跨境链路仍会让用户等待过久。
- 微信小程序目录 `wechat-miniprogram/` 已存在，脚手架检查通过，但目前更像演示 MVP，不是正式上架版本。
- 小程序 `appid` 仍为 `touristappid`，API 域名仍指向 Render，尚未切换到备案自有域名。
- 小程序的登录、注册、内容安全、预约、消息、身份切换、权限说明等仍需要补齐或强化；媒体上传已开始从 base64 JSON 改为 `wx.uploadFile` 文件上传链路。

建议路线：

1. 先修 P0 稳定性：后端、数据库、对象存储、域名、备份、发布检查。
2. 再补小程序核心功能闭环：登录注册、身份切换、关注互动、发布媒体、预约、消息、我的。
3. 最后补审核合规：隐私政策、用户协议、内容安全、举报后台、账号注销、权限说明。

## 2. 当前系统体检

### 2.1 当前部署

| 模块 | 当前状态 | 风险 |
| --- | --- | --- |
| 网页前端 | Cloudflare Pages: `https://fithub-cn.pages.dev/` | 中国大陆访问稳定性和小程序审核域名不确定 |
| 后端 API | Render: `https://fithub-app-1btg.onrender.com` | 冷启动、跨境链路、偶发慢响应 |
| 数据存储 | Supabase `fithub_app_state` | 本次检查发现远端不可达并进入 local fallback |
| 媒体存储 | Supabase Storage `fithub-media` | 本地环境未配置，线上依赖跨境对象存储 |
| 小程序 | `wechat-miniprogram/` 骨架 | 页面和能力不完整，未接正式小程序 AppID |

### 2.2 本次命令检查结果

已通过：

```bash
python3 scripts/check_miniprogram.py
python3 -m py_compile server.py
node --check app.js
```

正式提审前还必须通过生产配置检查：

```bash
python3 scripts/check_miniprogram.py --production
```

该检查会拦截：

- `project.config.json` 仍使用 `touristappid`
- `wechat-miniprogram/config.js` 仍指向 Render / Pages 测试域名
- `apiBase` 不是 HTTPS 或没有指向 `/api`

失败：

```bash
python3 scripts/deploy_smoke.py
```

失败原因：

```text
Backend is serving from local fallback; persistent writes are protected but production is degraded.
```

线上存储状态显示：

```text
storage.loadedFrom = local-fallback
storage.supabaseConfigured = true
storage.supabaseWritable = false
storage.remoteWriteProtected = true
metrics.real_profiles = 0
remoteRows.reachable = false
```

这意味着：后端现在没有稳定连上远端主数据。虽然代码做了“保护远端不被本地 fallback 覆盖”，但新用户数据、关注、消息、预约等在这个状态下不适合继续真实测试，更不适合上架。

## 3. P0 必须先修的问题

### P0-1. 后端与数据存储必须稳定

问题：

- 当前 Render 后端会冷启动，用户会等很久。
- 当前 Supabase 远端连接失败时会进入 local fallback。
- 小程序审核和真实用户使用都不能接受“有时等很久，有时数据不可写”。

修复方案：

1. 把生产 API 迁移到更稳定的国内云服务。
2. 使用备案自有域名，例如：
   - `api.fithub.cn`
   - `miniapi.fithub.cn`
3. 后端保留 `/healthz` 和 `/api/storage/status`。
4. 生产数据库必须长期可写，不能依赖本地 JSON fallback。
5. 发布前 smoke 必须失败即阻断，不允许降级状态发布。

建议技术路线：

- 短期最稳：腾讯云轻量应用服务器或 CVM 跑当前 Python 后端 + Nginx HTTPS。
- 存储短期：先修复 Supabase 连接并做完整备份。
- 存储中期：迁移到腾讯云数据库或其他国内可稳定访问数据库。
- 媒体：迁到腾讯云 COS + CDN，避免图片和视频跨境慢加载。

验收标准：

- `/healthz` 3 次连续返回 `200`，单次小于 1 秒。
- `/api/storage/status` 显示：
  - `loadedFrom` 不是 `local-fallback`
  - `supabaseWritable` 或新数据库 writable 为 `true`
  - `remoteWriteProtected` 为 `false`
  - `real_profiles` 不异常归零
- `npm run check:smoke` 必须通过。

### P0-2. 生产数据备份与恢复

问题：

- 当前已有多轮“用户消失、关注消失、消息消失”的历史问题。
- 小程序上架后，如果用户真实注册，任何数据丢失都会直接损害信任。

修复方案：

1. 上架前做一次线上数据完整快照。
2. 写一份迁移脚本或恢复脚本，能导出和导入：
   - accounts
   - profiles
   - follows
   - posts
   - comments
   - favorites
   - threads/messages
   - bookings
   - checkins
   - media metadata
3. 每次发布后自动检查核心计数不能异常下降。
4. 新增“数据体检脚本”，用于比对发布前后用户数、关注数、消息数、预约数。

验收标准：

- 发布前后 `real_profiles`、`real_follows`、`real_posts`、`real_threads` 不异常下降。
- 随机抽查一个手机号账号，退出/重进/换设备登录后身份、关注、消息、预约仍存在。
- 至少完成一次“备份恢复演练”。

### P0-3. 小程序正式域名与 AppID

问题：

- `wechat-miniprogram/project.config.json` 仍是 `touristappid`。
- `wechat-miniprogram/config.js` 仍指向 Render。
- 微信小程序后台需要配置合法域名，正式上架不建议使用当前 Render 临时后端域。

修复方案：

1. 替换真实小程序 AppID。
2. 配置正式 API 域名。
3. 在微信公众平台配置：
   - request 合法域名
   - uploadFile 合法域名
   - downloadFile 合法域名
4. 后端配置：
   - `FITHUB_WECHAT_MINIAPP_APP_ID`
   - `FITHUB_WECHAT_MINIAPP_APP_SECRET`
5. 小程序端关闭测试验证码展示，切换正式登录链路。

验收标准：

- 微信开发者工具真机预览能请求正式 API。
- 关闭“不校验合法域名”后仍能正常登录、发布、预约、上传。
- `project.config.json` 不再使用 `touristappid`。

## 4. P1 上架前必须补齐的产品功能

### P1-1. 小程序账号体系

当前状态：

- 小程序有微信登录入口。
- 有手机号验证码登录入口。
- 训练者快速注册仍偏测试化。

需要升级：

- 微信登录后绑定主账号。
- 手机号验证码登录后能恢复同一主账号下所有身份。
- 同一手机号可同时拥有健身爱好者、健身教练、健身房三种身份。
- 每种身份的数据环境互相独立：
  - 消息
  - 预约
  - 主页
  - 关注/粉丝
  - 动态
- 小程序内提供完整注册页，不再只有“训练者测试号”。

验收标准：

- A 手机注册，B 手机用同手机号/微信登录，能恢复同一账号。
- 切换身份即时响应。
- 教练身份收到的预约不出现在训练者身份里。
- 训练者身份的消息不被教练身份覆盖。

### P1-2. 小程序媒体上传

当前状态：

- 小程序用 `wx.chooseMedia` 选择图片/视频。
- 小程序发布页已改为通过 `wx.uploadFile` 调用 `/media/upload-file`。
- 后端已支持 `multipart/form-data` 文件上传，并复用现有对象存储/inline fallback/草稿清理逻辑。
- API 回归已覆盖 multipart 上传。
- 生产检查会拦截重新回到 base64 JSON 的媒体发布实现。

风险：

- 对象存储仍依赖当前后端环境变量和 Supabase/COS 等远端存储可达。
- 视频封面、上传进度、失败重试和草稿保留仍需要继续优化。
- 真实用户上传体验仍需在真机和弱网环境压测。

升级方案：

- 改为 `wx.uploadFile` 上传。
- 后端支持 multipart upload。
- 或后端签发临时上传凭证，直传对象存储。
- 上传前压缩图片，限制视频时长和大小。
- 发布按钮显示上传进度。
- 失败时可以重试，不丢草稿。

验收标准：

- 4 张图片能稳定上传并展示缩略图。
- 1 个短视频能稳定上传并生成封面。
- 断网/失败后有明确提示，草稿不丢。
- 动态流、收藏页、个人主页都能正常展示媒体。

### P1-3. 互动与消息

当前网页端已经做了大量互动体验优化，小程序端仍偏基础。

需要补齐：

- 关注即时反馈，不等待整页 reload。
- 点赞、收藏、评论即时反馈。
- 私信列表和私信详情页。
- 点击头像/名字进入对方主页。
- 对方主页支持关注、私信、拉黑、举报。
- 消息中心区分：
  - 赞
  - 评论
  - @我
  - 私信
  - 预约消息

验收标准：

- 点击关注后 300ms 内 UI 变化。
- 点赞/取消点赞可连续点击，不闪屏。
- 私信发送后立即显示在聊天窗口。
- 被拉黑后不能继续私信对方。

### P1-4. 预约核心闭环

当前状态：

- 小程序预约页有快速预约。
- 网页端已有教练/健身房可预约时间管理逻辑。

需要补齐：

- 教练/健身房在小程序端可发布可预约时间。
- 用户预约时可选择课程、价格、时间、地点。
- 教练/健身房可查看、确认、取消预约。
- 用户可查看待上课、本周待上课、历史订单。
- 预约消息进入消息中心。

验收标准：

- 教练发布一个时间段后，训练者能看到并预约。
- 预约后教练身份能收到订单。
- 教练确认后，训练者订单状态同步更新。

### P1-5. 定位与附近推荐

需要补齐：

- 小程序申请位置权限。
- 不授权时仍显示默认城市和手动城市选择。
- 授权后用真实经纬度计算附近健身房、教练、健身爱好者。
- 推荐关注按三类逻辑：
  - 可能认识/附近的人
  - 粉丝较多者
  - 评分较高者

验收标准：

- 首次授权定位后推荐列表变化。
- 拒绝定位后不影响基础浏览。
- 距离显示不出现明显错误。

## 5. P1 审核合规与运营安全

### P1-6. 内容安全

当前状态：

- 后端有轻量关键词审核和举报队列。
- 还不是正式微信内容安全链路。

需要补齐：

- 文本：动态、评论、私信接入微信或云厂商文本安全。
- 图片：头像、动态图片接入图片安全。
- 视频：动态视频接入视频安全或至少上传后异步审核。
- 举报入口：动态、评论、用户主页都要能举报。
- 管理后台：能处理举报、隐藏内容、封禁用户。

验收标准：

- 风险文本进入审核队列。
- 风险图片/视频不能公开展示或标记为审核中。
- 管理员能查看和处理待审核内容。

### P1-7. 隐私、协议和账号注销

上架前必须准备：

- 用户协议
- 隐私政策
- 第三方 SDK/服务说明
- 个人信息收集清单
- 权限使用说明：
  - 手机号
  - 相册/摄像头
  - 定位
  - 运动健康数据
  - 消息通知
- 账号注销入口
- 数据删除申请入口
- 客服联系方式

验收标准：

- 小程序内能打开隐私政策和用户协议。
- 用户能提交账号注销申请。
- 权限申请前有明确用途说明。

当前进展：

- 小程序已增加协议与隐私页面，覆盖隐私政策、用户协议和账号注销说明。
- “我的”页面已增加协议入口和账号注销申请入口。
- 后端已增加 `/api/account/delete-request`，用户提交后进入 `deletionRequests` 队列。
- 管理员审核接口已能查看和处理账号注销申请。
- 生产检查会拦截缺少合规页面或注销入口的小程序包。

剩余：

- 正式上线前需要替换为公司主体确认过的用户协议、隐私政策、个人信息清单和客服联系方式。
- 需要确定人工注销处理 SLA，以及未完成预约/争议订单时的处理规则。

## 6. P2 上架体验优化

### P2-1. 性能优化

需要做：

- 首屏骨架屏。
- 图片懒加载和缩略图。
- 首页、探索、我的页缓存优先显示。
- 后台同步失败时不清空现有 UI。
- API 请求加超时、重试和明确提示。
- 小程序端避免每次操作后全量 `bootstrap`。

验收标准：

- 首屏 2 秒内出现可读内容。
- 点赞/关注/收藏不整页闪动。
- 后端慢时显示轻提示，不出现空白页。

### P2-2. 小程序页面完整度

需要补齐页面：

- 个人主页
- 健身房主页
- 教练主页
- 私信详情
- 消息中心
- 我的关注/我的粉丝
- 收藏
- 健康数据
- 商城
- 预约时间管理
- 订单详情
- 设置/账号安全

当前五页可以作为主导航，但不能替代这些功能页。

### P2-3. 自动化测试与审核前检查

需要新增：

- 小程序 API smoke。
- 小程序页面结构检查。
- 生产域名检查。
- 内容安全模拟测试。
- 媒体上传大文件测试。
- 多身份切换测试。
- 跨设备登录测试。
- 发布前数据计数防回退测试。

建议命令：

```bash
npm run check:preflight
npm run check:smoke
npm run media:report
python3 scripts/final_acceptance.py
```

## 7. 建议执行阶段

### 阶段 A：上架前 P0 稳定性修复

目标：先让服务“不丢、不慢、不降级”。

任务：

1. 修复当前 Supabase 远端不可达问题。
2. 增强 `deploy_smoke.py`，把响应时间、profiles 数量异常下降纳入失败条件。
3. 增加发布前后数据计数对比脚本。
4. 明确国内 API 域名和部署方案。
5. 如走腾讯云，先完成 API 服务部署、HTTPS、备案域名接入。

完成标准：

- 线上 smoke 连续 3 次通过。
- 后端健康检查稳定小于 1 秒。
- 存储不再出现 `local-fallback`。

### 阶段 B：小程序正式基础链路

目标：小程序能用真实账号跑通主流程。

任务：

1. 替换真实 AppID。
2. 配置正式 API 域名。
3. 接微信登录和手机号绑定。
4. 完整注册三类身份。
5. 多身份切换与独立数据环境。
6. 首页、探索、我的、预约基础功能对齐网页端。

完成标准：

- 微信开发者工具真机预览能跑通：
  - 注册
  - 登录
  - 切身份
  - 关注
  - 发动态
  - 点赞/评论/收藏
  - 私信
  - 预约

### 阶段 C：媒体、内容安全与审核合规

目标：满足 UGC 产品审核和真实用户使用要求。

任务：

1. 小程序媒体上传改为 `wx.uploadFile` 或对象存储直传。
2. 接文本、图片、视频内容安全。
3. 做举报、拉黑、管理员处理闭环。
4. 补隐私政策、用户协议、账号注销。

完成标准：

- 风险内容不会直接公开。
- 用户可以举报和拉黑。
- 审核资料齐全。

### 阶段 D：内测与提审

目标：提交微信审核前把关键问题压掉。

任务：

1. 准备审核账号。
2. 准备审核说明。
3. 准备演示数据。
4. 10-20 人灰度试用。
5. 收集崩溃、卡顿、上传失败、登录失败问题。
6. 修复后提交审核。

完成标准：

- 连续 48 小时无 P0 数据问题。
- 主要流程真实用户可完成。
- 小程序后台无合法域名、隐私、类目阻塞。

## 8. 上架前阻断清单

以下任意一项未完成，不建议提审：

- `deploy_smoke.py` 失败。
- `/api/storage/status` 显示 `local-fallback`。
- 后端健康检查超过 3 秒。
- 小程序仍使用 `touristappid`。

## 国内后端迁移执行补充

当前仓库已准备腾讯云轻量/CVM 的发布包流程：

```bash
npm run release:tencent
```

生成包上传到腾讯云服务器后：

```bash
tar -xzf fithub-tencent-release-*.tar.gz
cd fithub-app-deploy/deploy/tencent-cloud
cp .env.production.example .env.production
./deploy.sh
```

绑定备案 HTTPS API 域名后，再执行：

```bash
npm run config:production -- \
  --api-origin https://api.yourdomain.com \
  --miniapp-appid wx你的真实小程序AppID
npm run check:production
```

`check:production` 通过前，不提交微信审核。
- 小程序 API 域名仍是 Render 临时域。
- 没有用户协议和隐私政策。
- 没有账号注销入口。
- 图片/视频/文本 UGC 没有内容安全策略。
- 媒体上传不能稳定成功。
- 多身份数据仍会串号。
- 退出重进或换设备登录后账号数据不稳定。

## 9. 官方参考入口

实际提交前仍以微信公众平台后台和官方文档为准：

- 微信小程序登录 code2Session：https://developers.weixin.qq.com/miniprogram/dev/OpenApiDoc/user-login/code2Session.html
- 微信小程序网络与合法域名：https://developers.weixin.qq.com/miniprogram/dev/framework/ability/network.html
- 微信小程序内容安全 msgSecCheck：https://developers.weixin.qq.com/miniprogram/dev/OpenApiDoc/sec-center/sec-check/msgSecCheck.html
- 微信小程序内容安全 mediaCheckAsync：https://developers.weixin.qq.com/miniprogram/dev/OpenApiDoc/sec-center/sec-check/mediaCheckAsync.html
- 微信小程序用户隐私保护指引：https://developers.weixin.qq.com/miniprogram/dev/framework/open-ability/userPrivacy.html

## 10. 我建议下一步先做什么

建议先从阶段 A 开始，顺序如下：

1. 彻底解决当前线上 `local-fallback` 降级。
2. 给发布检查增加“性能和数据计数防回退”。
3. 确认国内 API 域名和云服务迁移路径。
4. 再进入小程序正式功能补齐。

原因很简单：如果底层服务不稳，继续堆小程序页面会让问题越来越难查。先把地基打稳，后面所有功能升级才有意义。
