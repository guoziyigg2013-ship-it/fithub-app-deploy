# FitHub 国内生产存储与后端稳定化

## 当前策略

现阶段继续保留现有设计和固定入口：

- 前端固定域：`https://fithub-cn.pages.dev/`
- 后端 API：`https://fithub-app-1btg.onrender.com`
- 生产数据：Supabase `fithub_app_state`
- 媒体文件：Supabase Storage `fithub-media`

这套方案的核心目标不是“最终商用架构”，而是让当前试运行稳定：

- 更新后用户不消失
- 关注、动态、私信、预约、打卡不丢
- 后端冷启动或短暂失败时不覆盖远端生产数据
- 发布后能自动检查是否仍在使用持久化存储

## 已固化的稳定性保护

1. 主状态行
   - `primary` 保存当前完整业务状态
   - 所有注册、关注、动态、评论、收藏、私信、预约、打卡都会进入主状态

2. 小时备份行
   - `primary-backup-latest` 保存最近一次完整备份
   - `primary-backup-YYYYMMDDHH` 保存小时级快照
   - 默认保留最近 `96` 个小时备份

3. 手机号恢复行
   - `primary-phone-手机号` 保存该手机号相关的账号、身份、关注、动态参与、私信和预约
   - 即使主状态意外变旧，也能按手机号恢复关键用户关系

4. 本地 fallback 保护
   - 如果 Supabase 读取失败，后端只临时读取本地文件
   - 本地 fallback 不会覆盖远端生产状态
   - `/api/storage/status` 会显示 `local-fallback`

5. 发布后 smoke
   - `npm run check:smoke` 会检查固定前端、后端健康、存储状态和 bootstrap
   - 默认不允许生产后端退回本地 JSON

## 必要环境变量

Render 后端必须配置：

```text
SUPABASE_URL=https://你的项目ref.supabase.co
SUPABASE_SERVICE_ROLE_KEY=你的 service_role key
FITHUB_SUPABASE_TABLE=fithub_app_state
FITHUB_SUPABASE_ROW_ID=primary
FITHUB_MEDIA_BUCKET=fithub-media
FITHUB_PUBLIC_API_ORIGIN=https://fithub-app-1btg.onrender.com
```

建议配置：

```text
FITHUB_SUPABASE_TIMEOUT=12
FITHUB_SUPABASE_BACKUP_RETENTION=96
FITHUB_SUPABASE_PRUNE_INTERVAL_SECONDS=3600
FITHUB_IMAGE_UPLOAD_LIMIT_BYTES=10485760
FITHUB_VIDEO_UPLOAD_LIMIT_BYTES=8388608
FITHUB_THUMB_UPLOAD_LIMIT_BYTES=2097152
```

## 发布后验收

每次后端发布后执行：

```bash
npm run check:smoke
```

也可以手动打开：

```text
https://fithub-app-1btg.onrender.com/api/storage/status
```

必须重点看：

- `storage.supabaseConfigured` 为 `true`
- `storage.loadedFrom` 不应是 `local-fallback`
- `storage.remoteWriteProtected` 不应是 `true`
- `metrics.real_profiles` 不应异常归零

## 国内云迁移建议

后续真正服务中国大陆用户，建议按这个顺序迁移：

1. 前端
   - 从 Cloudflare Pages 迁到腾讯云 CloudBase 或 COS + CDN
   - 使用已备案自有域名

2. 后端
   - 短期：腾讯云 Lighthouse / CVM 跑当前 Python 服务
   - 中期：腾讯云 CloudBase 云托管 / 阿里云 SAE / 华为云 CCE
   - 保留 `/healthz` 和 `/api/storage/status` 作为健康检查

3. 数据库
   - 短期继续 Supabase，确保试运行不中断
   - 中期拆表到 PostgreSQL / MySQL：
     - `accounts`
     - `profiles`
     - `follows`
     - `posts`
     - `comments`
     - `post_favorites`
     - `threads`
     - `messages`
     - `bookings`
     - `checkins`

4. 对象存储
   - 迁到腾讯云 COS 或阿里云 OSS
   - 通过 CDN 提供图片、视频和缩略图
   - 上传时继续限制大小，并生成缩略图

## 暂不做的事

本阶段不强行把整份 JSON 改成多表数据库。原因是当前还在高频产品试错，贸然拆表会显著增加开发成本和迁移风险。

更稳妥的节奏是：

1. 当前阶段先把持久化、备份、诊断、发布检查稳住
2. 小程序/iOS 内测开始后观察真实数据增长
3. 当用户和动态量明显增长，再启动正式业务表迁移
