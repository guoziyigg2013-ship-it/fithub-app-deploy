# FitHub 腾讯云后端迁移手册

生成日期：2026-06-24

## 目标

把当前 FitHub API 从 Render 迁到国内更可控的后端域名，例如：

```text
https://api.yourdomain.com
```

这样做的目的：

- 避免 Render 冷启动和黑屏等待。
- 为微信小程序配置 `request 合法域名` 做准备。
- 让中国大陆用户访问后端更稳定。
- 保持前端和小程序现有设计不变，只替换 API 域名。

## 推荐路线

短期推荐：

1. 用本仓库根目录的 `Dockerfile` 构建 FitHub API 镜像。
2. 部署到腾讯云 CloudBase 云托管、腾讯云轻量应用服务器或 CVM。
3. 绑定已备案 HTTPS 域名，例如 `api.yourdomain.com`。
4. 前端 `config.js` 和小程序 `wechat-miniprogram/config.js` 都改成：

```js
apiBase: "https://api.yourdomain.com/api"
```

5. 用 `scripts/deploy_smoke.py` 做发布后检查。

腾讯云 CloudBase 云托管官方文档说明，它支持基于 Dockerfile 构建并运行 HTTP 服务；云托管服务应尽量无状态，数据需要放到外部数据库或对象存储。

参考：

- [腾讯云 CloudBase 云托管](https://cloud.tencent.com/document/product/1243)
- [微信小程序网络能力与合法域名](https://developers.weixin.qq.com/miniprogram/dev/framework/ability/network.html)

## 本地容器验证

先在本地构建：

```bash
docker build -t fithub-api:prelaunch .
```

本地启动：

```bash
docker run --rm \
  -p 10000:10000 \
  -e PORT=10000 \
  -e FITHUB_URL_PREFIX=/ \
  -e FITHUB_DATA_DIR=/data/fithub \
  -e SUPABASE_URL="https://你的项目ref.supabase.co" \
  -e SUPABASE_SERVICE_ROLE_KEY="你的service_role_key" \
  -e FITHUB_SUPABASE_TABLE=fithub_app_state \
  -e FITHUB_SUPABASE_ROW_ID=primary \
  fithub-api:prelaunch
```

检查：

```bash
curl http://127.0.0.1:10000/healthz
curl http://127.0.0.1:10000/api/storage/status?remote=1
```

必须确认：

- `storage.loadedFrom` 不是 `local-fallback`
- `storage.supabaseWritable` 是 `true`
- `storage.remoteWriteProtected` 是 `false`
- `remoteRows.reachable` 是 `true`

## 腾讯云部署环境变量

必填：

```text
PORT=10000
FITHUB_URL_PREFIX=/
FITHUB_DATA_DIR=/data/fithub
SUPABASE_URL=https://你的项目ref.supabase.co
SUPABASE_SERVICE_ROLE_KEY=你的service_role_key
FITHUB_SUPABASE_TABLE=fithub_app_state
FITHUB_SUPABASE_ROW_ID=primary
FITHUB_MEDIA_BUCKET=fithub-media
FITHUB_PUBLIC_API_ORIGIN=https://api.yourdomain.com
```

建议：

```text
FITHUB_SUPABASE_TIMEOUT=8
FITHUB_SUPABASE_REFRESH_COOLDOWN_SECONDS=30
FITHUB_SUPABASE_BACKUP_RETENTION=96
FITHUB_SUPABASE_PRUNE_INTERVAL_SECONDS=3600
FITHUB_IMAGE_UPLOAD_LIMIT_BYTES=10485760
FITHUB_VIDEO_UPLOAD_LIMIT_BYTES=8388608
FITHUB_THUMB_UPLOAD_LIMIT_BYTES=2097152
FITHUB_ADMIN_TOKEN=请生成强随机字符串
FITHUB_MEDIA_MAINTENANCE_TOKEN=请生成强随机字符串
```

## 发布后验收

后端上线后执行：

```bash
python3 scripts/deploy_smoke.py \
  --frontend-url https://fithub-cn.pages.dev/ \
  --backend-url https://api.yourdomain.com
```

上架前必须通过：

```bash
python3 scripts/check_miniprogram.py --production
python3 scripts/deploy_smoke.py --backend-url https://api.yourdomain.com
```

## 关键注意事项

- 不要把容器本地 `/data/fithub/shared_state.json` 当生产主数据。容器重建、扩容或迁移时，本地文件可能消失。
- 当前阶段可以继续用 Supabase 做远端主状态，但必须确保 `api.yourdomain.com` 的运行环境能稳定访问 Supabase。
- 如果 Supabase 在国内云环境仍不稳定，下一阶段要把数据拆到国内 PostgreSQL/MySQL，把媒体迁到腾讯云 COS。
- 微信小程序后台需要把 `https://api.yourdomain.com` 配置到合法域名，否则真机请求会失败。
