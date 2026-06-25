# FitHub 内容安全与举报后台

## 已实现范围

本阶段先完成上线前必须有的最小安全闭环：用户举报、文本/媒体风险入队、管理员受保护查看。

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

图片和视频上传后也会写入 `media.safety`：

- 默认 `FITHUB_MEDIA_SAFETY_PROVIDER=local`，先用本地规则兜底识别疑似违规文件名、异常格式和空媒体。
- 命中风险时写入 `moderationQueue`，`type=media`，`source=media-upload`。
- 后续接微信/腾讯云内容安全时，保持 `review_media_safety` 抽象不变，只替换 provider 实现。

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
- `summary.pendingDeletionRequests`
- `reports`
- `moderationQueue`
- `deletionRequests`
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

- 正式企业小程序 AppID 到位后，把 `FITHUB_MEDIA_SAFETY_PROVIDER` 从 `local` 切到微信/腾讯云图片视频审核 provider。
- 举报对象扩展到评论、私信和个人主页入口。
- 增加拉黑、隐藏内容、删除内容、封禁账号动作。
- 做一个真正的运营后台页面，而不是只靠 API。

## 账号注销申请

用户侧接口：

- `POST /api/account/delete-request`

请求示例：

```json
{
  "sessionId": "当前会话",
  "reason": "用户主动提交注销申请"
}
```

处理方式：

- 请求会进入 `deletionRequests` 队列。
- 管理员可在 `GET /api/admin/moderation?token=...` 里查看。
- 管理员可通过 `POST /api/admin/moderation/resolve` 处理，`kind` 传 `deletion`。
