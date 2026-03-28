# FitHub Render 上线说明

## 目标

把 FitHub 部署到固定域名，并支持后续 GitHub 推送自动更新。

## Render 配置

- Start Command: `python server.py`
- Health Check Path: `/healthz`
- Disk Mount Path: `/var/data`
- Disk Size: `1 GB`

## 环境变量

- `PORT=10000`
- `FITHUB_URL_PREFIX=/`  `可选，当前代码已默认根路径`
- `FITHUB_DATA_DIR=/var/data/fithub`  `建议保留，未填写时会优先尝试 /var/data/fithub`

## 自定义域名建议

推荐使用：

- `app.你的域名.com`

## 更新流程

1. 修改本仓库代码
2. 提交到 GitHub
3. 推送到 `main`
4. Render 自动重新部署

## 注意

`data/shared_state.json` 是运行期文件，不要提交到 GitHub。

如果没有挂载 Persistent Disk，即使页面能打开，注册、关注、评论、私信、预约等共享数据也可能在服务重启或重新部署后丢失。
