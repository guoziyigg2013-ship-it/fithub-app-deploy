# FitHub iOS 真机接入清单

## 目标

在 iPhone 上跑通：

1. 登录现有 FitHub 账户
2. 请求 Apple Health 权限
3. 读取 Apple Watch / Apple Health 数据
4. 同步到 FitHub 正式服务

## 当前工程位置

- 工程目录：`/Users/guoziyi/Documents/gpt/fitness-app-prototype/native-ios`
- 工程文件：`/Users/guoziyi/Documents/gpt/fitness-app-prototype/native-ios/FitHubNative.xcodeproj`
- 正式网址：`https://fithub-app-1btg.onrender.com/`

## 准备

1. 安装完整 Xcode
2. 打开：
   - `/Users/guoziyi/Documents/gpt/fitness-app-prototype/native-ios/FitHubNative.xcodeproj`
3. 在 `Signing & Capabilities` 中：
   - 选择自己的 Team
   - 把 Bundle ID 改成你自己的唯一值
   - 保留 `HealthKit`
4. 确认 `Info` 或配置里已经带有健康数据读取说明
   当前工程已经预置：
   - `NSHealthShareUsageDescription`

## 推荐先准备一组测试数据

至少准备下面任意一项：

- Apple Health 里已有体重
- Apple Health 里已有步数
- Apple Watch 里已有一次训练

如果 Apple Health 里完全没数据，App 也能运行，但你会看到同步结果为空。

## 真机要求

- iPhone 已登录 Apple ID
- iPhone 已打开 Apple Health
- 如果要测试 Apple Watch，手表需要已经与该 iPhone 配对

## Xcode 内操作顺序

1. 连接 iPhone 到 Mac
2. 在 Xcode 顶部选择你的 iPhone 真机
3. 第一次运行时，如果系统提示信任开发者签名，按系统引导完成
4. 确认 Build 没有签名报错

## 首次运行步骤

1. 选中真机运行 `FitHubNative`
2. 在 App 里填写：
   - 正式网址
   - 手机号
   - 身份
3. 点击 `登录 FitHub`
4. 确认页面显示“当前已连接 xxx”
5. 点击 `读取预览`
6. 系统弹出 Health 权限时允许读取
7. 确认页面出现：
   - 身高
   - 体重
   - 步数
   - 活跃卡路里
   - 最近训练
   中的任意一项
8. 点击 `同步到 FitHub`
9. 打开网页端 FitHub，确认该用户资料或动态已更新

## Apple Watch 测试方式

如果你要专门验证 Apple Watch：

1. 先戴着 Apple Watch 完成一次真实训练
2. 打开 iPhone 上的 Apple Health，确认训练已经入库
3. 再回到 `FitHubNative`
4. 点击 `读取预览`
5. 再点击 `同步到 FitHub`

注意：

- 当前原生 iOS 读取的是 `Apple Health`
- Apple Watch 数据会先进入 Apple Health
- FitHub 再从 iPhone 统一读取

## 成功判定

- App 中能看到身高、体重、体脂、静息心率、步数或最近训练
- 线上 FitHub 账户中出现新的健康数据或训练动态

## 快速回归测试

建议按这个最短链测：

1. 用已有健身爱好者手机号登录
2. 读取预览
3. 同步到 FitHub
4. 回网页看是否出现新的训练或身体数据
5. 退出 App 再打开，确认还能继续登录同一账户

## 如果失败先看这几项

- Bundle ID 是否唯一
- Team / 签名是否正确
- Health 权限是否允许
- 训练者身份是否存在
- 正式网址是否可访问

## 常见问题

### 1. 读不到任何数据

先确认 Apple Health 本身有没有数据，再确认授权是否已打开。

### 2. 登录成功但不能同步

当前只有 `健身爱好者` 身份支持健康同步；健身房和教练身份暂不支持。

### 3. Apple Watch 有训练，但 FitHub 里没看到

先确认 Apple Watch 训练已经在 iPhone 的 Apple Health 中出现；如果 Health 里都没有，FitHub 也读不到。
