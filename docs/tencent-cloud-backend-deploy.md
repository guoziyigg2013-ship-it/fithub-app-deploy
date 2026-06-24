# FitHub 腾讯云后端迁移手册

生成日期：2026-06-24

## 目标

把当前 FitHub API 从 Render 迁到国内更可控的后端域名，例如：

```text
https://api.yourdomain.com
```

正式试运行建议同时准备一个用户访问入口：

```text
https://app.yourdomain.com
```

当前 Python 服务会同时提供 Web 页面和 `/api`，所以 `api.yourdomain.com` 与 `app.yourdomain.com` 可以先反向代理到同一个腾讯云容器。小程序只需要把 `https://api.yourdomain.com` 加到合法域名；普通用户可以打开 `https://app.yourdomain.com`。

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
6. 用 `scripts/production_readiness.py` 做上架前生产配置检查。

拿到备案 API 域名、真实小程序 AppID、真实 Supabase Project URL 和 `service_role` 后，不要手工改多个文件。先执行正式切换预演：

```bash
npm run cutover:tencent -- \
  --api-origin https://api.yourdomain.com \
  --web-origin https://app.yourdomain.com \
  --miniapp-appid wx你的真实小程序AppID \
  --supabase-url https://你的项目ref.supabase.co \
  --supabase-service-role-key 你的真实service_role_key \
  --media-storage-provider cos \
  --cos-secret-id 你的腾讯云COSSecretId \
  --cos-secret-key 你的腾讯云COSSecretKey \
  --cos-region ap-guangzhou \
  --cos-bucket fithub-media-1250000000 \
  --cos-public-base-url https://media.yourdomain.com \
  --skip-release
```

预演通过后，再正式应用：

```bash
npm run cutover:tencent -- \
  --api-origin https://api.yourdomain.com \
  --web-origin https://app.yourdomain.com \
  --miniapp-appid wx你的真实小程序AppID \
  --supabase-url https://你的项目ref.supabase.co \
  --supabase-service-role-key 你的真实service_role_key \
  --media-storage-provider cos \
  --cos-secret-id 你的腾讯云COSSecretId \
  --cos-secret-key 你的腾讯云COSSecretKey \
  --cos-region ap-guangzhou \
  --cos-bucket fithub-media-1250000000 \
  --cos-public-base-url https://media.yourdomain.com \
  --apply \
  --write-env \
  --force
```

这个总控脚本会同时处理：

- `config.js` 的 `apiOrigin`
- `wechat-miniprogram/config.js` 的 `apiBase`
- `wechat-miniprogram/project.config.json` 的 `appid`
- `deploy/tencent-cloud/.env.production`
- `deploy/tencent-cloud/nginx-fithub.conf`
- `dist/fithub-tencent-release-*.tar.gz` 腾讯云发布包

如果只想单独切配置，仍可以使用较低层的脚本：

```bash
python3 scripts/configure_production.py \
  --api-origin https://api.yourdomain.com \
  --miniapp-appid wx你的真实小程序AppID \
  --dry-run
```

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

## 腾讯云轻量服务器 / CVM 快速部署模板

仓库已经提供一个基础模板：

```text
deploy/tencent-cloud/docker-compose.yml
deploy/tencent-cloud/.env.production.example
deploy/tencent-cloud/deploy.sh
deploy/tencent-cloud/nginx-fithub.conf.example
```

### 1. 在本地构建干净发布包

不要上传整个工作区。先在本地生成只包含 Git 跟踪代码和部署模板的发布包：

```bash
npm run release:tencent
```

输出位置类似：

```text
dist/fithub-tencent-release-20260624-120000.tar.gz
dist/fithub-tencent-release-20260624-120000.tar.gz.manifest.json
```

发布包会自动排除：

- 真实 `.env` 文件
- 运行态数据 `data/`
- 生产快照 `backups/`
- `node_modules/`
- Playwright 产物和临时文件

部署时在服务器上执行：

```bash
tar -xzf fithub-tencent-release-*.tar.gz
cd fithub-app-deploy/deploy/tencent-cloud
cp .env.production.example .env.production
```

推荐不要手填 `.env.production`，而是回到仓库根目录用生成器创建：

```bash
cd ../..
python3 scripts/init_tencent_env.py \
  --api-origin https://api.yourdomain.com \
  --web-origin https://app.yourdomain.com \
  --supabase-url https://你的真实项目ref.supabase.co \
  --supabase-service-role-key '你的真实service_role_key' \
  --media-storage-provider cos \
  --cos-secret-id '你的腾讯云COSSecretId' \
  --cos-secret-key '你的腾讯云COSSecretKey' \
  --cos-region ap-guangzhou \
  --cos-bucket fithub-media-1250000000 \
  --cos-public-base-url https://media.yourdomain.com \
  --output deploy/tencent-cloud/.env.production \
  --nginx-output deploy/tencent-cloud/nginx-fithub.conf \
  --print-redacted
```

生成器会自动创建长随机 `FITHUB_ADMIN_TOKEN` 和 `FITHUB_MEDIA_MAINTENANCE_TOKEN`。如果文件已存在，需要明确加 `--force` 才会覆盖。

然后启动：

```bash
cd deploy/tencent-cloud
chmod +x deploy.sh
./deploy.sh
```

`deploy.sh` 会在启动前自动执行：

- `tencent_server_doctor.py`：检查服务器依赖、磁盘、端口、env、Docker Compose 配置。
- `tencent_cloud_preflight.py`：检查占位域名、假 key、短 token 和生产配置。

如果发现明显问题，会直接停止，不会带病启动。

如果域名、HTTPS 和 Nginx 已经全部配置好，可以强制在部署后检查公网 API 和远程存储：

```bash
FITHUB_DEPLOY_CHECK_PUBLIC=1 ./deploy.sh
```

如果你用 Nginx 或腾讯云负载均衡做 HTTPS，反向代理到：

```text
http://127.0.0.1:10000
```

Nginx 可以参考：

```text
deploy/tencent-cloud/nginx-fithub.conf.example
```

如果使用上面的 `--nginx-output`，会自动生成已替换域名的：

```text
deploy/tencent-cloud/nginx-fithub.conf
```

如果传入了 `--web-origin https://app.yourdomain.com`，生成的 Nginx 会同时包含：

```nginx
server_name api.yourdomain.com app.yourdomain.com;
```

绑定域名后，确认：

```bash
curl https://app.yourdomain.com/
curl https://api.yourdomain.com/healthz
curl https://api.yourdomain.com/api/storage/status?remote=1
```

再跑一次带线上域名的预检：

```bash
python3 ../../scripts/tencent_server_doctor.py \
  --check-public \
  --allow-running-service

python3 ../../scripts/tencent_cloud_preflight.py \
  --backend-url https://api.yourdomain.com
```

确认国内 API 正常后，再回到本地仓库执行正式配置切换。推荐使用总控命令，避免漏改小程序 AppID 或 API 地址：

```bash
npm run cutover:tencent -- \
  --api-origin https://api.yourdomain.com \
  --web-origin https://app.yourdomain.com \
  --miniapp-appid wx你的真实小程序AppID \
  --supabase-url https://你的项目ref.supabase.co \
  --supabase-service-role-key 你的真实service_role_key \
  --apply \
  --write-env \
  --force
```

然后提交、发布前端和小程序代码。

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
FITHUB_MEDIA_STORAGE_PROVIDER=cos
FITHUB_TENCENT_COS_SECRET_ID=你的腾讯云COSSecretId
FITHUB_TENCENT_COS_SECRET_KEY=你的腾讯云COSSecretKey
FITHUB_TENCENT_COS_REGION=ap-guangzhou
FITHUB_TENCENT_COS_BUCKET=fithub-media-1250000000
FITHUB_TENCENT_COS_PUBLIC_BASE_URL=https://media.yourdomain.com
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
  --frontend-url https://app.yourdomain.com/ \
  --backend-url https://api.yourdomain.com
```

上架前必须通过：

```bash
python3 scripts/check_miniprogram.py --production
python3 scripts/tencent_cloud_preflight.py \
  --env-file deploy/tencent-cloud/.env.production \
  --backend-url https://api.yourdomain.com
python3 scripts/tencent_server_doctor.py \
  --env-file deploy/tencent-cloud/.env.production \
  --check-public \
  --allow-running-service
python3 scripts/production_readiness.py --backend-url https://api.yourdomain.com
python3 scripts/production_readiness.py --backend-url https://api.yourdomain.com --require-cos-media
python3 scripts/deploy_smoke.py --frontend-url https://app.yourdomain.com/ --backend-url https://api.yourdomain.com
```

最后跑一次写入链路验收，确认不是“页面能打开但用户数据不稳”：

```bash
python3 scripts/production_write_acceptance.py \
  --backend-url https://api.yourdomain.com \
  --phone 你的内部验收手机号 \
  --verification-code 注册验证码 \
  --login-verification-code 登录验证码
```

如果后端仍是开发验证码模式，脚本会自动使用 `debugCode`。正式生产短信模式下，需要输入验收手机号收到的真实验证码。

如果 `production_readiness.py` 仍提示 `onrender.com`、`pages.dev`、`touristappid` 或 Supabase `NXDOMAIN`，说明当前仍是试运行配置，不要提交微信审核。

也可以直接用 npm 命令：

```bash
npm run config:production -- \
  --api-origin https://api.yourdomain.com \
  --miniapp-appid wx你的真实小程序AppID

npm run check:production
```

## 关键注意事项

- 不要把容器本地 `/data/fithub/shared_state.json` 当生产主数据。容器重建、扩容或迁移时，本地文件可能消失。
- 当前阶段可以继续用 Supabase 做远端主状态，但必须确保 `api.yourdomain.com` 的运行环境能稳定访问 Supabase。
- 国内生产媒体建议直接使用腾讯云 COS + CDN。`/api/storage/status?remote=1` 的 `media.storageProvider` 应该显示 `cos`，否则不要提交小程序审核。
- 如果 Supabase 在国内云环境仍不稳定，下一阶段要把主业务数据也拆到国内 PostgreSQL/MySQL。
- 微信小程序后台需要把 `https://api.yourdomain.com` 配置到合法域名，否则真机请求会失败。
