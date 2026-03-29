# FitHub Native Health Sync API

## 接口

- `POST /api/health/native-sync`

## 用途

给原生 iOS / Android App 上传真实健康数据与训练记录。  
网页端不直接读设备，而是展示同步后的结果。

## 请求体

```json
{
  "sessionId": "native-session-id",
  "profileId": "enthusiast-xxxx",
  "source": "apple-healthkit",
  "deviceName": "iPhone + Apple Health",
  "devices": ["Apple Health", "Apple Watch"],
  "metrics": {
    "heightCm": 178,
    "weightKg": 72.4,
    "bodyFat": 17.8,
    "restingHeartRate": 58,
    "stepCount": 9362,
    "activeEnergyBurned": 684.0
  },
  "workouts": [
    {
      "externalId": "healthkit-workout-uuid",
      "workoutType": "running",
      "sportId": "run",
      "sportLabel": "户外跑步",
      "durationMinutes": 42,
      "distanceKm": 6.3,
      "activeEnergyBurned": 402.0,
      "startedAt": "2026-03-29T08:20:00Z",
      "endedAt": "2026-03-29T09:02:00Z"
    }
  ]
}
```

## 服务端行为

- 更新训练者的身高、体重、体脂、静息心率等身体数据
- 更新 `connectedDevices / healthSource / deviceSyncedAt`
- 将新训练写入 `checkins`
- 同时生成对应动态
- 以 `externalId` 去重，避免同一条训练重复导入

## 当前支持来源

- `apple-healthkit`
- `apple-watch`
- `xiaomi-watch`
- `xiaomi-scale`
- `health-connect`

## 说明

第一阶段重点是先接通 `Apple Health / Apple Watch -> iPhone 原生 App -> FitHub API`。  
小米和 Android 路线后续会基于 `Health Connect` 或正式合作接口继续补。
