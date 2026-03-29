# FitHub Deploy Repo

这个目录是 `FitHub` 的独立发布仓库版本，用来：

- 推送到 GitHub
- 接入 Render 自动部署
- 绑定固定域名
- 保留多人互动数据

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

详细初始化 SQL 和步骤见：

- [docs/fithub-supabase-setup.md](./docs/fithub-supabase-setup.md)
