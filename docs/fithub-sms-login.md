# FitHub 验证码登录接入说明

FitHub 当前已经支持手机号验证码登录/注册校验。

正式环境推荐使用腾讯云短信：

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

如果还没正式开通短信，也可以先用调试模式联调：

- `FITHUB_SMS_DEV_MODE=true`

这时页面仍会显示验证码入口，但后端不会真的发短信，而是直接把测试验证码通过接口返回给前端提示，方便先验证登录流程。

## Render 环境变量示例

```text
FITHUB_SMS_PROVIDER=tencent
FITHUB_TENCENT_SMS_SECRET_ID=你的SecretId
FITHUB_TENCENT_SMS_SECRET_KEY=你的SecretKey
FITHUB_TENCENT_SMS_APP_ID=你的SmsSdkAppId
FITHUB_TENCENT_SMS_SIGN_NAME=你的短信签名
FITHUB_TENCENT_SMS_TEMPLATE_ID=你的验证码模板ID
FITHUB_TENCENT_SMS_REGION=ap-guangzhou
FITHUB_SMS_CODE_LENGTH=6
FITHUB_SMS_CODE_TTL_SECONDS=300
FITHUB_SMS_RESEND_SECONDS=60
```

## 模板建议

腾讯云短信模板建议至少包含：

1. 验证码本身
2. 有效分钟数

例如模板变量顺序：

1. `{1}` 验证码
2. `{2}` 有效分钟数

服务端当前会按这个顺序发送模板参数。

## 当前登录规则

1. 同一设备登录过后，会优先用本机保存的账户凭证自动恢复。
2. 换设备时，可以用手机号 + 验证码登录。
3. 同一个手机号 + 同一个身份，不会重复创建多个独立用户，而是回到原有身份记录。
4. 同一个手机号可以绑定多个身份角色，但它们会被归到同一个稳定账户下面，避免数据混乱。
