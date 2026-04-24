# FitHub Deploy Repo

这个目录是 `FitHub` 的独立发布仓库版本，用来：

- 推送到 GitHub
- 接入 Render 自动部署
- 绑定固定域名
- 保留多人互动数据

当前已经有一个中国试运行静态入口：

- `https://fithub-cn.pages.dev/`

这个入口由 `Cloudflare Pages` 提供静态页面，避免用户首次打开先撞到 `Render` 黑色唤醒页；数据仍然走当前的 `Render + Supabase` 后端。

## 本地运行

```bash
python3 server.py --port 8010
```

本地默认使用：

- 页面入口：`/`
- API 入口：`/api`

如果你想兼容旧的子路径访问，也可以显式设置：

- `FITHUB_URL_PREFIX=/fitness-app-prototype`

正式部署建议保持根路径：

- 页面入口：`/`
- API 入口：`/api`

## 中国试运行入口更新

如果你修改了前端并且要重新发布中国站静态入口，在这个目录执行：

```bash
./deploy-cn-pages.sh
```

如果你想发布到另一个 Pages 项目名：

```bash
./deploy-cn-pages.sh your-project-name
```

## 部署

1. 在这个目录执行 `git add .`
2. 创建 GitHub 仓库并推送 `main`
3. 在 Render 里用 Blueprint / Web Service 连接仓库
4. 读取当前目录下的 `render.yaml`
5. 配置自定义域名，例如 `app.你的域名.com`

## 数据持久化

运行态共享数据不会提交到 Git：

- `data/shared_state.json`

正式环境数据保存在：

- `/var/data/fithub/shared_state.json`

如果没有挂载 Render Persistent Disk，数据会写进实例本地文件系统，服务重启或重建后可能丢失。

## Supabase 模式

如果你暂时没有 Render 付费 Disk，可以直接把持久化切到 `Supabase`。

当前服务端已经支持：

- 优先使用 `Supabase`
- 如果没有配置 `Supabase`，自动回退到本地 JSON

需要在 Render 环境变量里设置：

- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`

可选：

- `FITHUB_SUPABASE_TABLE=fithub_app_state`
- `FITHUB_SUPABASE_ROW_ID=primary`
- `FITHUB_MEDIA_BUCKET=fithub-media`

详细初始化 SQL 和步骤见：

- [docs/fithub-supabase-setup.md](./docs/fithub-supabase-setup.md)

## 媒体对象存储

当前图片/视频与头像已经支持走 `Supabase Storage`：

- 注册头像优先上传到对象存储
- 动态里的图片/视频优先上传到对象存储
- 动态图片会同步生成缩略图
- 动态视频会同步生成封面缩略图
- 媒体支持详情预览，收藏页和动态页可直接放大查看
- 发布弹窗里移除未发布的媒体时，会尝试同步清理对象存储草稿文件
- 已提供对象存储巡检/清理脚本，可识别未被引用的陈旧媒体对象
- 如果对象存储暂时不可用，会自动回退到旧的内联方式，不会直接把发布流程打断

默认 bucket：

- `fithub-media`

如果你想改名字，可以设置：

- `FITHUB_MEDIA_BUCKET`

当前默认大小限制：

- 图片：`10 MB`
- 视频：`8 MB`
- 缩略图：`2 MB`

对象存储巡检：

```bash
npm run media:report
```

删除超过 24 小时、且未被引用的媒体对象：

```bash
npm run media:clean
```

如果要让外部定时任务触发线上清理，可以在 Render 设置：

- `FITHUB_MEDIA_MAINTENANCE_TOKEN`

然后用 `POST /api/media/maintenance` 调用，传入：

```json
{ "token": "同一个维护 token", "ageHours": 24, "delete": true }
```

## 验证码登录

当前已经支持手机号验证码登录/注册校验。

如果你要在正式环境启用腾讯云短信，请在 Render 环境变量里设置：

- `FITHUB_SMS_PROVIDER=tencent`
- `FITHUB_TENCENT_SMS_SECRET_ID`
- `FITHUB_TENCENT_SMS_SECRET_KEY`
- `FITHUB_TENCENT_SMS_APP_ID`
- `FITHUB_TENCENT_SMS_SIGN_NAME`
- `FITHUB_TENCENT_SMS_TEMPLATE_ID`

可选：

- `FITHUB_TENCENT_SMS_REGION=ap-guangzhou`
- `FITHUB_SMS_CODE_LENGTH=6`
- `FITHUB_SMS_CODE_TTL_SECONDS=300`
- `FITHUB_SMS_RESEND_SECONDS=60`
- `FITHUB_SMS_CODE_SALT`

如果只是先联调流程，也可以先开：

- `FITHUB_SMS_DEV_MODE=true`

详细说明见：

- [docs/fithub-sms-login.md](./docs/fithub-sms-login.md)

## 回归与发布自检

本地发布前推荐直接跑：

```bash
npm run check:preflight
```

它会依次执行：

- `node --check app.js`
- `python3 -m py_compile server.py`
- API 回归测试
- Playwright UI 主链回归

部署到固定域和 Render 后，再跑：

```bash
npm run check:smoke
```

默认检查：

- `https://fithub-cn.pages.dev/`
- `https://fithub-app-1btg.onrender.com`

完整发布前后顺序见：

- [docs/fithub-release-runbook.md](./docs/fithub-release-runbook.md)
