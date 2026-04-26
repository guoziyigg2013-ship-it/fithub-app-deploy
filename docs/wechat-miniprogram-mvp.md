# FitHub 微信小程序 MVP

## 项目位置

小程序代码在：

```text
wechat-miniprogram/
```

导入微信开发者工具时，选择这个目录作为项目根目录。

## 当前页面

- `pages/home/index`：首页，展示附近健身房和教练。
- `pages/discover/index`：探索，包含推荐关注、关注动态、点赞、收藏、举报。
- `pages/publish/index`：发布动态，支持文字、图片、视频选择和上传。
- `pages/booking/index`：预约，展示预约记录并支持快速预约。
- `pages/me/index`：我的，支持微信登录、手机号验证码登录、训练者快速注册。

## API 配置

当前小程序默认请求：

```text
https://fithub-app-1btg.onrender.com/api
```

配置位置：

```text
wechat-miniprogram/config.js
```

后续换成备案自有域名时，只需要改这里。

## 微信登录

后端接口：

```text
POST /api/auth/wechat-mini-login
```

正式链路按微信官方 `auth.code2Session` 流程实现：

```text
https://developers.weixin.qq.com/miniprogram/dev/OpenApiDoc/user-login/code2Session.html
```

正式环境需要配置：

```text
FITHUB_WECHAT_MINIAPP_APP_ID=你的小程序 AppID
FITHUB_WECHAT_MINIAPP_APP_SECRET=你的小程序 AppSecret
```

测试环境可以开启：

```text
FITHUB_WECHAT_MINIAPP_DEV_MODE=true
```

测试模式不会访问微信服务器，只用于 API 回归和本地流程联调。

## 微信后台必须配置

在微信公众平台的小程序后台配置服务器域名：

- `request合法域名`：后端 API 域名
- `uploadFile合法域名`：后端 API 域名
- `downloadFile合法域名`：媒体 CDN 域名或后端 API 域名

当前临时后端域名是：

```text
https://fithub-app-1btg.onrender.com
```

正式上线建议替换为已备案自有域名。

## 后续要补

- 微信手机号授权能力。
- 微信内容安全接口。
- 小程序订阅消息。
- 更完整的教练/健身房主页。
- 发布页视频封面压缩与上传进度。
