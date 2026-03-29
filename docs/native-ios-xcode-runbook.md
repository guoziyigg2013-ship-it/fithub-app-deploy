# FitHub iPhone 真机运行 Runbook

## 适用范围

这份 runbook 用来把 `native-ios` 工程在真 iPhone 上跑起来，并验证：

1. 能登录现有 FitHub 账户
2. 能请求 Apple Health 权限
3. 能读取真实健康数据预览
4. 能把数据同步回正式服务

## 工程入口

- 工程目录：`/Users/guoziyi/Documents/gpt/fitness-app-prototype/native-ios`
- Xcode 工程：`/Users/guoziyi/Documents/gpt/fitness-app-prototype/native-ios/FitHubNative.xcodeproj`
- 正式网址：`https://fithub-app-1btg.onrender.com/`

## 运行前准备

1. Mac 已安装完整 Xcode
2. iPhone 已用数据线或无线调试连接到 Mac
3. iPhone 已登录 Apple ID
4. iPhone 上已经打开过 `健康` App
5. Apple Health 里至少有一项真实数据
   - 体重
   - 步数
   - 一次 Apple Watch 训练

## 第一次打开工程要做的事

1. 用 Xcode 打开 `FitHubNative.xcodeproj`
2. 选中左侧 `FitHubNative` target
3. 打开 `Signing & Capabilities`
4. 设置：
   - `Team`：选你自己的开发团队
   - `Bundle Identifier`：改成你自己的唯一值
     例：`com.yourname.fithubnative`
5. 确认 `HealthKit` capability 已存在

## 真机运行顺序

1. 在 Xcode 顶部设备列表里选你的 iPhone
2. 按运行
3. 如果出现签名或信任提示：
   - 按 Xcode 引导完成
   - iPhone 上如提示“未受信任的开发者”，到系统设置里信任
4. 首屏先看 `iPhone 真机首跑检查`
   应至少看到：
   - 服务地址
   - 当前身份
   - Apple Health 权限状态
   - 最近同步状态

## App 内测试步骤

1. 填正式网址
   - `https://fithub-app-1btg.onrender.com/`
2. 选择身份
   - 建议先选 `健身爱好者`
3. 输入已存在的测试手机号
4. 点 `登录 FitHub`
5. 点 `检查权限`
6. 点 `读取预览`
7. 第一次会弹系统健康权限框，选择允许
8. 看到预览后，再点 `同步到 FitHub`

## 成功判定

满足以下任意两项，说明真机链路已经通了：

1. 预览页读到了身高、体重、步数、活跃卡路里中的任意一项
2. 预览页显示最近训练数量大于 0
3. 同步后网页端 FitHub 的该用户资料或动态出现新训练数据
4. 再次打开 App，账户连接和最近同步状态还在

## 授权异常时怎么处理

如果 `Apple Health` 一直显示未授权：

1. 在 App 内点 `打开系统设置`
2. 进入当前 App 的设置页
3. 确认健康访问权限已打开
4. 回到 App 再点一次 `检查权限`
5. 然后重新 `读取预览`

## 最短回归链路

每次你改完 iOS 代码，可以只跑下面这条：

1. 打开 App
2. 刷新状态
3. 登录 FitHub
4. 读取预览
5. 同步到 FitHub
6. 回网页检查该用户是否出现新健康数据

## 注意

- Apple Watch 数据不是直接被 FitHub 读取，而是先进入 iPhone 上的 `健康` App，再由 FitHub Native 统一读取
- 当前只有 `健身爱好者` 身份支持同步健康数据
- 模拟器不适合验证真实 HealthKit 数据，真机优先
