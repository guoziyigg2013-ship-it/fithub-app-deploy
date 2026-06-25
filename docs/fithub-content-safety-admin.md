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

浏览器后台：

- `admin.html`
- 输入 `FITHUB_ADMIN_TOKEN` 后可查看举报、待审核内容、注销申请和最近处理记录。
- 支持直接将举报、审核队列或注销申请标记为“处理完成”或“忽略”。
- 支持对风险内容作者执行“限制账号/解除限制”，被限制身份不能继续发布动态、评论、点赞、收藏、私信、关注、预约或排课。
- 支持对风险动态执行“隐藏动态/恢复动态”，隐藏后用户端主页、探索、收藏和通知不再展示该动态，也不能继续点赞、收藏或评论。

管理员 token 使用：

- 优先读取 `FITHUB_ADMIN_TOKEN`
- 如果未设置，则回退到 `FITHUB_MEDIA_MAINTENANCE_TOKEN`

接口：

- `GET /api/admin/moderation?token=...`
- `POST /api/admin/moderation/resolve`
- `POST /api/admin/content/moderation`
- `POST /api/admin/profile/moderation`

`GET /api/admin/moderation` 返回：

- `summary.openReports`
- `summary.pendingReview`
- `summary.pendingDeletionRequests`
- `reports`
- `moderationQueue`
- `deletionRequests`
- `hiddenPosts`
- `suspendedProfiles`
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

`POST /api/admin/content/moderation` 请求示例：

```json
{
  "token": "你的后台 token",
  "targetType": "post",
  "targetId": "post-xxxx",
  "status": "hidden",
  "reason": "运营后台隐藏"
}
```

## 后续必须补齐

- 正式企业小程序 AppID 到位后，把 `FITHUB_MEDIA_SAFETY_PROVIDER` 从 `local` 切到微信/腾讯云图片视频审核 provider。
- 举报对象扩展到评论、私信和个人主页入口。
- 如需满足更强合规要求，再补硬删除内容动作；当前默认优先隐藏，方便申诉恢复。
- 正式提审前可把账号限制动作升级为更细的分级处罚，例如仅禁言、暂停预约或永久封禁。

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
