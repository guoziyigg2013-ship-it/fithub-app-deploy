# FitHub Android / Health Connect 真机接入清单

## 目标

在 Android 真机上跑通：

1. 登录现有 FitHub 账户
2. 连接 Health Connect
3. 读取运动和身体数据
4. 同步回 FitHub

## 准备

1. 安装 Android Studio
2. 打开目录：
   - `/Users/guoziyi/Documents/gpt/fitness-app-prototype/native-android`
3. 等待 Gradle Sync 完成
4. Android 设备安装或更新 `Health Connect`

## 真机步骤

1. 运行 `native-android`
2. 输入：
   - 正式网址
   - 手机号
   - 身份
3. 点击 `登录 FitHub`
4. 点击 `授权 Health Connect`
5. 允许读取训练、步数、体重、体脂、心率等数据
6. 点击 `读取预览`
7. 点击 `同步到 FitHub`

## 成功判定

- App 中能显示健康预览
- FitHub 中能看到同步后的训练或身体数据

## 小米设备说明

- 如果小米设备数据已经进了系统健康平台，优先直接走 `Health Connect`
- 如果要走小米健康云直连，需要正式合作权限

## 如果失败先看这几项

- Android 版本是否支持 Health Connect
- Health Connect 是否已安装 / 已更新
- 登录的是否是已有训练者身份
- 正式网址是否可访问
