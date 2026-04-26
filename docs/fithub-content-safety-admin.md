# FitHub 内容安全与举报后台

## 已实现范围

本阶段先完成上线前必须有的最小安全闭环：用户举报、文本风险入队、管理员受保护查看。

## 用户侧能力

- 动态卡片支持举报。
- 举报会写入 `reports`。
- 同一个用户对同一个对象重复举报时，会更新原举报原因，避免刷出大量重复记录。
- 举报成功后前端会给即时提示。

## 内容审核入队

以下内容会进行轻量文本扫描：

- 动态正文
- 评论
- 私信

命中风险词后，内容不会直接阻断用户发布，但会写入 `moderationQueue`，方便测试期不打断正常体验，同时保留后台处理入口。

## 管理员接口

管理员 token 使用：

- 优先读取 `FITHUB_ADMIN_TOKEN`
- 如果未设置，则回退到 `FITHUB_MEDIA_MAINTENANCE_TOKEN`

接口：

- `GET /api/admin/moderation?token=...`
- `POST /api/admin/moderation/resolve`

`GET /api/admin/moderation` 返回：

- `summary.openReports`
- `summary.pendingReview`
- `reports`
- `moderationQueue`
- `adminActions`

`POST /api/admin/moderation/resolve` 请求示例：

```json
{
  "token": "你的后台 token",
  "kind": "report",
  "id": "report-xxxx",
  "status": "resolved",
  "note": "已处理"
}
```

## 后续必须补齐

- 图片和视频接入云厂商内容安全审核。
- 举报对象扩展到评论、私信和个人主页入口。
- 增加拉黑、隐藏内容、删除内容、封禁账号动作。
- 做一个真正的运营后台页面，而不是只靠 API。
