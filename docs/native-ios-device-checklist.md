# FitHub iOS 真机接入清单

## 目标

在 iPhone 上跑通：

1. 登录现有 FitHub 账户
2. 请求 Apple Health 权限
3. 读取 Apple Watch / Apple Health 数据
4. 同步到 FitHub 正式服务

## 准备

1. 安装完整 Xcode
2. 打开：
   - `/Users/guoziyi/Documents/gpt/fitness-app-prototype/native-ios/FitHubNative.xcodeproj`
3. 在 `Signing & Capabilities` 中：
   - 选择自己的 Team
   - 把 Bundle ID 改成你自己的唯一值
   - 保留 `HealthKit`

## 真机要求

- iPhone 已登录 Apple ID
- iPhone 已打开 Apple Health
- 如果要测试 Apple Watch，手表需要已经与该 iPhone 配对

## 首次运行步骤

1. 连接 iPhone 到 Mac
2. 选中真机运行 `FitHubNative`
3. 在 App 里填写：
   - 正式网址
   - 手机号
   - 身份
4. 点击 `登录 FitHub`
5. 点击 `读取预览`
6. 系统弹出 Health 权限时允许读取
7. 点击 `同步到 FitHub`

## 成功判定

- App 中能看到身高、体重、体脂、静息心率、步数或最近训练
- 线上 FitHub 账户中出现新的健康数据或训练动态

## 如果失败先看这几项

- Bundle ID 是否唯一
- Team / 签名是否正确
- Health 权限是否允许
- 训练者身份是否存在
- 正式网址是否可访问
