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
- `FITHUB_URL_PREFIX=/`
- `FITHUB_DATA_DIR=/var/data/fithub`

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
