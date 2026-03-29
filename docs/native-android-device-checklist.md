# FitHub Android / Health Connect 真机接入清单

## 目标

在 Android 真机上跑通：

1. 登录现有 FitHub 账户
2. 连接 Health Connect
3. 读取运动和身体数据
4. 同步回 FitHub

## 当前工程位置

- 工程目录：`/Users/guoziyi/Documents/gpt/fitness-app-prototype/native-android`
- 正式网址：`https://fithub-app-1btg.onrender.com/`

## 准备

1. 安装 Android Studio
2. 打开目录：
   - `/Users/guoziyi/Documents/gpt/fitness-app-prototype/native-android`
3. 等待 Gradle Sync 完成
4. Android 设备安装或更新 `Health Connect`
5. 手机打开：
   - USB 调试
   - 如果是小米 / OPPO / vivo 等机型，也建议打开开发者模式下的安装调试授权

## 推荐先准备一组测试数据

至少准备下面任意一项：

- Health Connect 已经能看到步数
- Health Connect 已经能看到体重
- Health Connect 已经能看到一条训练记录

如果系统健康平台里完全没有数据，App 也能运行，但同步结果会是空的。

## 真机步骤

1. 运行 `native-android`
2. 输入：
   - 正式网址
   - 手机号
   - 身份
3. 点击 `登录 FitHub`
4. 如果页面出现：
   - `打开 Health Connect`
   - 或 `安装或更新 Health Connect`
   先点它进入系统设置或 Play 商店
5. 回到 App 后点击 `授权 Health Connect`
6. 允许读取训练、步数、体重、体脂、心率等数据
7. 点击 `读取预览`
8. 点击 `同步到 FitHub`

## Android Studio 内建议顺序

1. 打开工程后先等 `Gradle Sync` 全部完成
2. 在设备选择器里选中真机
3. 第一次运行先不要急着同步
   先确认页面能打开、按钮能点击
4. 再执行：
   - 登录 FitHub
   - 打开或安装 Health Connect
   - 授权
   - 读取预览
   - 同步到 FitHub

## Health Connect 页面上应该看到什么

正常情况下，FitHub Android 原生页会出现其中一种按钮：

- `打开 Health Connect`
- `安装或更新 Health Connect`

这两个按钮的意义是：

- 已安装：直接去健康设置
- 未安装或版本过旧：直接去 Google Play

## 成功后你应该看到什么

1. 页面里出现健康预览
   - 身高
   - 体重
   - 体脂
   - 心率
   - 步数
   - 活跃卡路里
   - 最近训练数量
2. 网页版 FitHub 中出现更新后的身体数据或训练动态

## 成功判定

- App 中能显示健康预览
- FitHub 中能看到同步后的训练或身体数据

## 快速回归测试

建议按这个最短链测：

1. 登录已有健身爱好者手机号
2. 打开或安装 Health Connect
3. 读取预览
4. 同步到 FitHub
5. 回网页看该用户数据是否更新
6. 退出 App 再打开，确认还能继续登录同一账户

## 小米设备说明

- 如果小米设备数据已经进了系统健康平台，优先直接走 `Health Connect`
- 如果要走小米健康云直连，需要正式合作权限

## 如果失败先看这几项

- Android 版本是否支持 Health Connect
- Health Connect 是否已安装 / 已更新
- 是否已经通过 App 内按钮成功打开 Health Connect 设置或商店
- 登录的是否是已有训练者身份
- 正式网址是否可访问

## 常见问题

### 1. 页面显示“当前设备暂不支持 Health Connect”

优先检查：

- Android 版本
- Google Play 服务
- Health Connect 是否可安装

### 2. 能授权，但读取不到数据

通常是因为系统健康平台里本身还没有数据。

### 3. 小米手表或小米秤明明有数据

先看这些数据有没有进入 `Health Connect`。  
如果没有，当前阶段 FitHub 也读不到；这不代表后面不能支持，只是现阶段优先走系统健康平台这条公开可用路线。
