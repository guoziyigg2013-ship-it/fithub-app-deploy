# FitHub 微信小程序上架前审查与大升级方案

生成日期：2026-06-24

## 0. 审查结论

当前 FitHub 不建议直接提交微信小程序审核。

不是因为产品方向不行，而是因为现在仍存在几个会直接影响审核和真实用户使用的底层问题：

- 生产后端仍在 Render，存在冷启动、跨境访问和后端唤醒等待问题。
- 当前线上存储状态为 `local-fallback`，远端 Supabase 不可达，新用户、关注、消息、预约、打卡等数据存在试运行风险。
- 微信小程序项目仍使用 `touristappid`，API 域名仍指向 Render，不满足正式上架配置。
- 小程序已有 MVP 骨架，但还没有达到“真实用户可长期使用”的产品完整度。
- UGC 内容安全、图片/视频审核、举报处理、管理员后台、账号注销处理规则还需要补齐。

建议先做一轮“上架前大升级”，目标不是堆新功能，而是把底层稳定性、正式小程序配置、数据持久化、内容安全和核心闭环全部打稳。

## 1. 本次实测结果

### 1.1 已执行命令

```bash
python3 scripts/deploy_smoke.py
python3 scripts/check_miniprogram.py
python3 scripts/check_miniprogram.py --production
python3 -m unittest discover -s tests/api -p 'test_*.py' -v
python3 -m py_compile server.py
node --check app.js
```

### 1.2 通过项

- `https://fithub-cn.pages.dev/` 前端壳返回 `200`，本次响应约 `0.18s`。
- `https://fithub-app-1btg.onrender.com/healthz` 返回 `ok`，本次响应约 `0.30s`。
- 小程序普通脚手架检查通过：

```bash
python3 scripts/check_miniprogram.py
```

- 本地 API 回归全部通过：

```text
Ran 40 tests in 3.093s
OK
```

- `server.py` 和 `app.js` 语法检查通过。

### 1.3 阻断项

#### 阻断 1：生产 smoke 失败

```bash
python3 scripts/deploy_smoke.py
```

失败原因：

```text
Backend is serving from local fallback; persistent writes are protected but production is degraded.
host=gjhyfcqqrtpratguvlqc.supabase.co
hasServiceRoleKey=True
remoteError=<urlopen error [Errno -2] Name or service not known>
```

线上 `/api/storage/status?remote=1` 当前关键信息：

```json
{
  "ok": false,
  "status": "degraded",
  "storage": {
    "loadedFrom": "local-fallback",
    "supabaseConfigured": true,
    "supabaseWritable": false,
    "remoteWriteProtected": true
  },
  "metrics": {
    "real_profiles": 0,
    "real_follows": 0,
    "real_posts": 0,
    "real_bookings": 0,
    "real_threads": 0,
    "real_checkins": 0
  },
  "remoteRows": {
    "reachable": false
  }
}
```

解释：

- 线上后端没有稳定读到远端主数据。
- 代码已经保护了“本地 fallback 不覆盖远端数据”，这是好事。
- 但只要仍是 `local-fallback`，就不适合继续真实用户测试，更不适合上架。

#### 阻断 2：小程序生产检查失败

```bash
python3 scripts/check_miniprogram.py --production
```

失败原因：

```text
Production mini program must use a real AppID, not touristappid.
```

当前小程序配置：

- `/wechat-miniprogram/project.config.json` 仍是 `touristappid`
- `/wechat-miniprogram/config.js` 仍是 `https://fithub-app-1btg.onrender.com/api`

正式上架前必须替换为真实小程序 AppID 和已备案 HTTPS API 域名。

#### 阻断 3：`npm test` 不存在

项目没有 `npm test` 脚本。正确命令是：

```bash
npm run check:syntax
npm run test:api
npm run check:preflight
npm run check:smoke
npm run check:final
```

后续发布门禁应统一用这些命令，避免误以为项目没有测试。

## 2. 上架前总目标

本轮大升级完成后，FitHub 应达到下面标准：

1. 中国大陆用户打开稳定，没有 Render 黑屏/长时间唤醒。
2. 用户注册、登录、关注、消息、预约、打卡、动态不会因为部署更新而丢失。
3. 小程序能用真实 AppID、真实备案域名、真实 HTTPS API 跑通主流程。
4. 图片/视频上传走对象存储和缩略图，不再依赖本地或大 base64。
5. UGC 文本、图片、视频、评论、私信有内容安全策略。
6. 用户可以举报、拉黑、注销账号，后台可以处理。
7. 每次发布前后有自动化门禁，失败就不发布。

## 3. P0：必须先修的底层稳定性

### P0-1. 迁出 Render 作为正式生产后端

当前问题：

- Render 会出现应用唤醒页和冷启动。
- 中国大陆访问 Render 与 Supabase 都不稳定。
- 微信小程序正式上架需要稳定 HTTPS 合法域名，不建议继续使用 Render 域名做生产 API。

建议方案：

- 短期：腾讯云轻量应用服务器 / CVM / CloudBase 云托管部署当前 Python API。
- 域名：使用已备案域名，例如 `api.fithub.cn` 或你最终确定的业务域名。
- HTTPS：配置正式证书。
- 健康检查保留 `/healthz`。
- 发布后固定跑：

```bash
python3 scripts/deploy_smoke.py --backend-url https://api.yourdomain.com
```

验收标准：

- `/healthz` 连续 3 次小于 `1s`。
- `/api/bootstrap` 小于 `2s`。
- 不再出现 Render 黑屏或长时间唤醒提示。

### P0-2. 生产数据库稳定化

当前问题：

- 现在核心状态仍是 Supabase 单行 JSON 主状态。
- 线上 Supabase 当前不可达，后端降级为 `local-fallback`。
- 这会直接导致用户感觉“账号/关注/消息消失”。

建议分两步：

#### 第一步：立刻修复当前远端主状态

- 查明线上 DNS/网络为什么访问不到 `gjhyfcqqrtpratguvlqc.supabase.co`。
- 确认 `SUPABASE_URL`、`SUPABASE_SERVICE_ROLE_KEY`、表名、Row ID 都正确。
- 跑通 `/api/storage/status?remote=1`。
- 确认 `loadedFrom != local-fallback`。

#### 第二步：上架前迁到更适合国内的数据库

推荐生产模型：

- `accounts`
- `profiles`
- `sessions`
- `follows`
- `posts`
- `post_media`
- `comments`
- `favorites`
- `threads`
- `messages`
- `bookings`
- `availability_slots`
- `checkins`
- `reports`
- `moderation_queue`

短期也可以继续保留 JSON 主状态作为过渡，但必须满足：

- 远端可写。
- 有发布前后计数对比。
- 有自动备份。
- 有恢复演练。

验收标准：

- 新账号注册后，后端重启、重新部署、换设备登录，账号仍存在。
- 关注关系、私信、动态、预约、打卡全部不丢。
- `real_profiles`、`real_follows`、`real_posts` 不会在发布后异常归零。

### P0-3. 生产媒体存储与 CDN

当前状态：

- 后端已支持 `/api/media/upload-file` 和 multipart 上传。
- 小程序已改为 `wx.uploadFile`。
- 但生产对象存储仍依赖当前 Supabase Storage 环境和跨境链路。

建议方案：

- 中国大陆试运行优先迁到腾讯云 COS + CDN。
- 上传图片自动压缩并生成缩略图。
- 视频限制大小和时长，生成封面。
- 上传失败保留草稿，不让用户重写。

验收标准：

- 头像上传后刷新不丢。
- 图文动态、视频动态、收藏页、个人主页全部能稳定显示媒体。
- 弱网下上传失败有明确提示和重试。
- 线上媒体读取不依赖慢跨境资源。

## 4. P0：小程序生产配置

### P0-4. 真实 AppID 与合法域名

必须完成：

1. 用真实小程序 AppID 替换 `touristappid`。
2. 小程序后台配置合法域名：
   - request 合法域名
   - uploadFile 合法域名
   - downloadFile 合法域名
3. `wechat-miniprogram/config.js` 改为正式 API：

```js
apiBase: "https://api.yourdomain.com/api"
```

4. 微信开发者工具里关闭“不校验合法域名”，真机仍能正常运行。

验收标准：

```bash
python3 scripts/check_miniprogram.py --production
```

必须通过。

### P0-5. 真实登录链路

必须完成：

- 微信登录 `code2Session`
- 手机号验证码登录
- 微信账号与手机号主账号绑定
- 一个手机号对应一个主账号
- 同一主账号可拥有健身爱好者、教练、健身房三个身份
- 三个身份的数据环境独立，切换方便

验收标准：

- A 手机注册，B 手机登录同手机号/微信后能恢复同一账号。
- 健身爱好者消息不被教练身份覆盖。
- 教练收到的预约不会混到健身爱好者里。
- 手动退出登录后，页面真的进入“登录/注册选择”状态。

## 5. P1：上架前核心产品闭环

### P1-1. 首页与附近推荐

必须做到：

- 定位授权前默认厦门/手动城市。
- 定位授权后用真实经纬度推荐附近用户、教练、健身房。
- 推荐关注按三类逻辑：
  - 可能认识/附近的人
  - 粉丝较多者
  - 评分较高者
- 已关注对象从推荐区移除，点击关注立即反馈。

验收标准：

- 关注按钮 300ms 内变状态。
- 慢网络下不会诱导用户重复点击。
- 健身爱好者、教练、健身房三类身份关注逻辑一致。

### P1-2. 探索与动态流

必须做到：

- 已关注对象动态按时间倒序展示。
- 关注健身爱好者后，其动态也进入时间线。
- 纯文字动态也可收藏。
- 图片/视频动态可正常展示、收藏、评论、私信。
- 点击头像/名字进入主页。

验收标准：

- 点赞、收藏、评论即时反馈，不闪屏。
- 图片/视频不长时间空白。
- 刷新后收藏数量和状态仍正确。

### P1-3. 私信与消息中心

必须做到：

- 所有人默认可私信，除非被对方拉黑。
- 消息列表类似成熟聊天产品：头像、未读红点、最近一条消息。
- 聊天详情左右气泡对齐，发送后立即显示。
- 消息按身份隔离。
- 消息中心包含：
  - 赞
  - 评论
  - @我
  - 私信
  - 预约消息

验收标准：

- 发消息不等待网络返回也先出现气泡。
- 切换身份后只看到当前身份相关消息。
- 对方主页有拉黑/举报入口。

### P1-4. 预约与订单

必须做到：

- 教练/健身房可发布可预约时间。
- 训练者可选择课程、价格、时间、地点并预约。
- 教练/健身房能查看别人给我的预约。
- 训练者能查看自己发起的预约和订单。
- 预约消息进入消息中心。

验收标准：

- 教练发布一个时间段后，训练者能看到并预约。
- 预约后教练端立即看到订单。
- 订单状态切换不会丢。

### P1-5. 打卡、GPS 与健康

必须做到：

- GO 后进入运动记录页。
- 运动中不可切换运动项目。
- 户外运动采集真实 GPS 点。
- 有足够 GPS 点时显示真实轨迹。
- 室内运动不显示轨迹。
- 打卡数据进入健康中心。
- 健康中心显示运动趋势、跑步、行走、骑行、瑜伽、步数、摄氧量等模块。

验收标准：

- 结束打卡不卡死。
- GPS 权限拒绝时有明确提示，不影响室内打卡。
- 健康页能看到本周/本月趋势。

### P1-6. 商城

必须做到：

- 商品列表、分类、详情、咨询购买入口可用。
- 商城先不接支付，先走咨询/私信。
- 商品数据后续可由后台管理。

验收标准：

- 用户能打开商城、切分类、进入商品咨询。

## 6. P1：审核合规和安全

### P1-7. 内容安全

FitHub 属于 UGC 社区/互动平台，必须有内容安全闭环。

必须覆盖：

- 动态文本
- 评论
- 私信
- 头像
- 动态图片
- 动态视频
- 用户昵称/简介

建议方案：

- 小程序端提交前做基础长度和类型校验。
- 后端接微信内容安全或腾讯云内容安全。
- 风险内容进入审核队列，不直接公开。
- 管理员可以隐藏、删除、封禁。

验收标准：

- 风险文本不会直接公开。
- 图片/视频上传后有审核状态。
- 用户可举报内容和用户。
- 管理员可处理举报。

### P1-8. 隐私、协议、注销和客服

必须准备：

- 用户协议
- 隐私政策
- 个人信息收集清单
- 第三方 SDK/服务说明
- 权限用途说明：
  - 手机号
  - 头像昵称
  - 相册/摄像头
  - 定位
  - 运动健康数据
  - 消息通知
- 账号注销入口
- 数据删除申请
- 客服联系方式

当前进展：

- 小程序已有法律页面。
- 后端已有 `/api/account/delete-request`。
- 管理员接口能看到注销申请。

仍需补齐：

- 正式公司主体确认过的协议内容。
- 客服联系方式。
- 注销处理 SLA。
- 未完成预约/争议订单的注销规则。

## 7. P2：性能和体验专项

### P2-1. 首屏和慢后端体验

问题来源：

- 后端冷启动或远端存储不可达时，用户会看到长时间空白或“正在唤醒”。

升级方案：

- 首页、探索、我的优先显示本地缓存快照。
- 后台静默刷新，不要先清空页面。
- 接口超时后明确提示“网络慢，正在重试”，不要白屏。
- 后端稳定后再取消大面积唤醒提示。

验收标准：

- 首屏 2 秒内有可读内容。
- 后端慢时不白屏。
- 页面不因一次 API 慢而整屏闪动。

### P2-2. 图片和头像加载

升级方案：

- 真实图片必须走缩略图。
- 头像使用小尺寸裁剪。
- 首屏媒体使用明确尺寸，避免布局跳动。
- 图片失败时使用干净默认头像，不出现丑陋占位。
- 列表图片懒加载，首屏图片高优先级。

验收标准：

- 探索流首屏图片不明显延迟。
- 默认头像简洁，不出现黄色脸或破图。
- 图片加载失败不导致界面抖动。

### P2-3. 操作即时反馈

必须覆盖：

- 关注
- 点赞
- 收藏
- 评论
- 私信
- 提交注册资料
- 发布动态
- 预约
- 打卡结束

原则：

- 点击后 UI 先变化。
- 网络失败再回滚并提示。
- 不用锁按钮制造“没反应”的错觉。

验收标准：

- 主要操作 300ms 内有视觉反馈。
- 慢网络模拟下不会重复提交。

## 8. 自动化门禁

### 8.1 本地发布前

```bash
npm run check:syntax
npm run test:api
npm run check:preflight
```

必须通过。

### 8.2 小程序生产配置

```bash
python3 scripts/check_miniprogram.py --production
```

必须通过。

### 8.3 固定域发布后

```bash
npm run check:smoke
```

必须通过。

生产 smoke 必须检查：

- 前端可访问
- 后端健康
- 后端不是 `local-fallback`
- 远端存储可写
- 真实用户数量不异常归零
- `bootstrap` 正常

### 8.4 真机手工验收

每次提审前至少过一遍：

1. 新用户注册。
2. 老用户登录。
3. 切换身份。
4. 关注一个人。
5. 发图文动态。
6. 点赞、评论、收藏。
7. 发私信。
8. 教练发布预约时间。
9. 训练者预约。
10. 打卡一次。
11. 查看健康。
12. 提交举报。
13. 进入协议/隐私/注销入口。

### 8.5 生产数据快照

每次上架前大升级必须先做一次生产快照：

```bash
FITHUB_ADMIN_TOKEN=你的管理员token npm run snapshot:prod
```

脚本会调用：

```text
GET /api/admin/export
```

并在本地生成：

```text
backups/fithub-production-snapshot-YYYYMMDD-HHMMSSZ.json
```

升级完成后，用新快照对比旧快照：

```bash
FITHUB_ADMIN_TOKEN=你的管理员token \
python3 scripts/production_snapshot.py \
  --compare backups/fithub-production-snapshot-旧版本时间.json
```

默认会拦截这些关键指标下降：

- `real_profiles`
- `phone_profiles`
- `accounts`
- `real_follows`
- `real_posts`
- `real_bookings`
- `real_threads`
- `real_checkins`

如果运营上确实删除了内容，可以用 `--allow-decrease real_posts:1` 显式允许小范围下降；否则不要绕过。

## 9. 建议执行顺序

### 阶段 A：生产地基修复

目标：先让服务稳定、不丢数据。

任务：

1. 备份当前线上 Supabase 和本地数据。
2. 修复或迁移当前 `local-fallback` 问题。
3. 部署国内后端 API。
4. 绑定备案 HTTPS API 域名。
5. 对象存储迁移到 COS/OSS/CDN。
6. 跑通 `deploy_smoke.py`。

完成标准：

- 连续 3 次 `npm run check:smoke` 通过。
- `/api/storage/status` 不再 degraded。
- 新注册用户、关注、消息、动态在重新部署后不丢。

### 阶段 B：小程序正式化

目标：小程序可真机跑通主流程。

任务：

1. 替换真实 AppID。
2. 配置合法域名。
3. 微信登录 + 手机号绑定。
4. 三身份注册与切换。
5. 小程序首页、探索、发布、预约、我的对齐网页核心能力。
6. 小程序媒体上传稳定化。

完成标准：

- 关闭合法域名校验豁免后真机仍可用。
- `check_miniprogram.py --production` 通过。

### 阶段 C：安全合规和后台

目标：满足 UGC 审核和运营要求。

任务：

1. 接内容安全。
2. 完善举报、拉黑、隐藏、封禁。
3. 完善账号注销和隐私协议。
4. 管理后台最小可用。

完成标准：

- 风险内容不直接公开。
- 管理员能处理举报和注销申请。

### 阶段 D：灰度内测与提审

目标：提交微信审核。

任务：

1. 准备审核账号和审核说明。
2. 10-20 人真机灰度。
3. 连续 48 小时无 P0 数据问题。
4. 修复灰度问题。
5. 提交审核。

## 10. 不建议提审的红线

以下任一项存在，就不建议提审：

- 线上仍显示 `local-fallback`。
- `deploy_smoke.py` 失败。
- 小程序仍是 `touristappid`。
- API 域名仍是 Render。
- 没有合法域名配置。
- 没有正式隐私政策和用户协议。
- 没有账号注销入口。
- 没有内容安全策略。
- 图片/视频上传不稳定。
- 用户登录后身份、关注、消息会消失。
- 教练/健身房无法管理预约时间。

## 11. 官方参考

实际提审前以微信公众平台后台和官方文档为准：

- 微信小程序网络与合法域名：https://developers.weixin.qq.com/miniprogram/dev/framework/ability/network.html
- 微信小程序登录 code2Session：https://developers.weixin.qq.com/miniprogram/dev/OpenApiDoc/user-login/code2Session.html
- 微信小程序内容安全 msgSecCheck：https://developers.weixin.qq.com/miniprogram/dev/OpenApiDoc/sec-center/sec-check/msgSecCheck.html
- 微信小程序内容安全 mediaCheckAsync：https://developers.weixin.qq.com/miniprogram/dev/OpenApiDoc/sec-center/sec-check/mediaCheckAsync.html
- 微信小程序用户隐私保护指引填写说明：https://developers.weixin.qq.com/miniprogram/dev/framework/user-privacy/

## 12. 我建议同意后第一步做什么

我建议先做阶段 A，不要先继续堆页面。

第一步具体执行：

1. 新建生产数据备份与导出脚本。
2. 修复当前线上 `local-fallback`，如果 Render 环境无法稳定访问 Supabase，就直接迁后端到国内云。
3. 把 `deploy_smoke.py` 扩展成真正的上架门禁：
   - 存储必须远端可写
   - 响应时间必须达标
   - 真实用户计数不能异常下降
   - 小程序生产配置必须通过
4. 准备正式 API 域名接入小程序。

原因很简单：只要底层存储和后端不稳，上面所有功能越做越多，问题会越来越难查。先把地基打稳，FitHub 才能像成熟产品一样稳定升级。
