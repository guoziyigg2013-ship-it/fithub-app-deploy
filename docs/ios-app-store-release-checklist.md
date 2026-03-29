# FitHub iOS 上架清单

## 当前已经准备好的部分

这套原生 iOS 工程里，我已经先替你补好了这些上架前基础项：

1. 原生工程：
   - `/Users/guoziyi/Documents/gpt/fitness-app-prototype/native-ios/FitHubNative.xcodeproj`
2. App 显示名：
   - `FitHub`
3. App Icon：
   - 已生成 `1024 x 1024` 营销图标和 iPhone 所需尺寸
4. HealthKit 权限说明：
   - `NSHealthShareUsageDescription`
5. 真机运行说明：
   - [native-ios-xcode-runbook.md](/Users/guoziyi/Documents/gpt/fitness-app-prototype/docs/native-ios-xcode-runbook.md)

## 你还需要在 Apple 侧完成的事

### 1. Apple Developer Program

必须保证你的 Apple Developer Program 会员状态有效，否则不能正式上传和发布。

### 2. 在 App Store Connect 创建 App

到 App Store Connect 新建一个 App，至少要填：

- App 名称：`FitHub`
- 平台：`iOS`
- 主要语言：建议 `简体中文`
- Bundle ID：和 Xcode 里最终使用的完全一致
- SKU：你自己定义一个唯一值

### 3. 在 Xcode 里完成签名

在 `Signing & Capabilities` 里完成：

- Team
- 唯一的 Bundle Identifier
- 保留 `HealthKit`

### 4. 准备 App Store 元数据

至少要准备：

- 副标题
- 关键词
- 应用描述
- 隐私政策 URL
- 支持 URL
- 年龄分级问卷
- App 隐私数据收集说明

### 5. 准备截图

建议至少准备：

- iPhone 6.9 英寸截图
- iPhone 6.5 英寸截图

如果你先走 TestFlight 内测，这一步可以稍后再补，但正式提审前必须准备好。

### 6. 从 Xcode Archive 上传

在 Xcode 里：

1. 选 `Any iOS Device`
2. `Product -> Archive`
3. 打开 `Organizer`
4. 选择 `Distribute App`
5. 上传到 App Store Connect

### 7. 先走 TestFlight，再提审

我建议你先内部测试，再正式提交审核：

1. 上传 build
2. 在 TestFlight 里加内部测试成员
3. 验证登录、同步 Apple Health、同步到网页端
4. 没问题后再提交审核

## 2026 年你必须注意的官方要求

Apple 官方当前写明：

- 自 `2026-04-28` 起，上传到 App Store Connect 的 iOS App 必须使用 `Xcode 26` 或更高版本，并且用 `iOS 26 SDK` 或更高版本构建

这意味着你正式上传时，不能再用过旧 Xcode。

## 官方资料

- 新建 App：
  [Add a new app](https://developer.apple.com/help/app-store-connect/create-an-app-record/add-a-new-app/)
- 上传构建：
  [Upload builds](https://developer.apple.com/help/app-store-connect/manage-builds/upload-builds/)
- 管理 App 隐私：
  [Manage app privacy](https://developer.apple.com/help/app-store-connect/manage-app-information/manage-app-privacy/)
- 提交审核：
  [Submit an app](https://developer.apple.com/help/app-store-connect/manage-submissions-to-app-review/submit-an-app/)
- 近期上架要求：
  [Upcoming Requirements](https://developer.apple.com/cn/news/upcoming-requirements/)

## 我建议你的最短路径

先不要直接冲正式上架，按这个顺序最稳：

1. 用 Xcode 在真机跑通
2. 用 TestFlight 内测
3. 我们再补 App Store 描述、截图、隐私文案
4. 最后再提交审核
