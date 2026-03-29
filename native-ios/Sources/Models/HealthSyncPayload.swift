import Foundation

struct HealthPreview {
    let heightCm: Int?
    let weightKg: Double?
    let bodyFatPercentage: Double?
    let restingHeartRate: Int?
    let stepCountToday: Int?
    let activeEnergyToday: Double?
    let workouts: [NativeWorkoutPayload]
}
