# FitHub 原生设备接入第一阶段

## 目标

先把“真实健康数据”接入链路搭起来，而不是继续在网页里做模拟按钮。

## 第一阶段范围

- iOS 原生 App 读取 `HealthKit`
- 把 Apple Watch 已写入 Health 的训练记录同步到 FitHub
- 更新训练者的真实身体数据
- 把同步训练直接沉淀成 FitHub 打卡和动态

## 为什么先做 iOS

Apple Watch 的训练数据最终会回流到 iPhone 的 `Apple Health`，  
所以第一阶段只要原生 iPhone App 能接 `HealthKit`，就能把 Apple Watch 数据一起带进来。

## Android / 小米路线

建议拆成两条：

1. Android 通用路线：`Health Connect`
2. 小米专有路线：在拿到正式合作权限后，再接小米健康云

如果小米手表数据已经同步到系统健康平台，优先走系统健康平台，维护成本更低。

## 本地目录

- `/Users/guoziyi/Documents/gpt/fitness-app-prototype/native-ios`

## 当前已经完成

- 后端新增 `POST /api/health/native-sync`
- 支持导入身体指标
- 支持导入训练记录并去重
- 新建 iOS SwiftUI + HealthKit 骨架

## 下一步

- 真正生成 Xcode 工程并在 iPhone 上跑通授权
- 增加 Apple 登录 / 短信登录
- 评估 Android 原生项目和 Xiaomi 路线
