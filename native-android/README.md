## FitHub Native Android

这套目录是 FitHub 的 Android 原生接入骨架，目标是把真实健康数据从系统健康平台带回现有 FitHub 账户。

### 当前路线

1. 优先接 `Health Connect`
2. 如果小米设备数据已经同步进系统健康平台，仍优先走 `Health Connect`
3. 小米健康云官方合作接口单独保留为后续扩展位

### 为什么先这样做

`Health Connect` 是 Android 官方健康数据汇聚入口，适合作为：

- 步数
- 卡路里
- 训练记录
- 身高体重
- 体脂
- 心率

的统一读取层。

### 目录说明

- `settings.gradle.kts`
- `build.gradle.kts`
- `app/`
  - Compose 主界面
  - Health Connect 权限与读取
  - FitHub API 上传
  - Xiaomi 预留 provider

### 运行前准备

1. 安装 Android Studio
2. 打开本目录
3. 同步 Gradle
4. 在 Android 设备安装并启用 Health Connect

更适合直接照着跑的联调文档在这里：

- [native-device-quickstart.md](/Users/guoziyi/Documents/gpt/fitness-app-prototype/docs/native-device-quickstart.md)
- [native-android-device-checklist.md](/Users/guoziyi/Documents/gpt/fitness-app-prototype/docs/native-android-device-checklist.md)

### 当前真机体验

- 先用 `手机号 + 身份` 登录现有 FitHub 账户
- App 会根据设备状态显示：
  - `打开 Health Connect`
  - 或 `安装或更新 Health Connect`
- 已安装时优先拉起 Health Connect 设置
- 未安装或需要升级时优先跳转 Google Play
- 完成后再授权并读取真实健康数据

### Xiaomi 路线说明

当前项目里已经放了：

- `XiaomiSyncProvider.kt`

它现在只作为结构化占位层。原因是小米健康云官方文档明确说明：

- 现阶段仅对小米生态链企业及合作伙伴开放
- 需要 AppID / AppKey / OAuth token

所以正式直连要等合作权限。  
在那之前，如果小米手表或秤的数据能进系统健康平台，优先直接读 `Health Connect`。
