import Foundation
import HealthKit

final class HealthKitSyncService {
    private let healthStore: HKHealthStore
    private let isoFormatter = ISO8601DateFormatter()

    init(healthStore: HKHealthStore) {
        self.healthStore = healthStore
    }

    func loadPreview(days: Int = 30) async throws -> HealthPreview {
        async let rawHeight = latestQuantity(.height, unit: HKUnit.meterUnit(with: .centi))
        async let rawWeight = latestQuantity(.bodyMass, unit: HKUnit.gramUnit(with: .kilo))
        async let rawBodyFat = latestQuantity(.bodyFatPercentage, unit: HKUnit.percent())
        async let rawRestingHeartRate = latestQuantity(.restingHeartRate, unit: HKUnit.count().unitDivided(by: .minute()))
        async let rawStepCountToday = cumulativeQuantityToday(.stepCount, unit: HKUnit.count())
        async let rawActiveEnergyToday = cumulativeQuantityToday(.activeEnergyBurned, unit: HKUnit.kilocalorie())
        async let workouts = recentWorkouts(since: Calendar.current.date(byAdding: .day, value: -days, to: Date()) ?? Date())

        let heightCm = try await rawHeight.map { Int(round($0)) }
        let weightKg = try await rawWeight
        let bodyFat = try await rawBodyFat.map { $0 * 100.0 }
        let restingHeartRate = try await rawRestingHeartRate.map { Int(round($0)) }
        let stepCountToday = try await rawStepCountToday.map { Int(round($0)) }
        let activeEnergyToday = try await rawActiveEnergyToday
        let recent = try await workouts

        return HealthPreview(
            heightCm: heightCm,
            weightKg: weightKg,
            bodyFatPercentage: bodyFat,
            restingHeartRate: restingHeartRate,
            stepCountToday: stepCountToday,
            activeEnergyToday: activeEnergyToday,
            workouts: recent
        )
    }

    func makeSyncRequest(sessionId: String, profileId: String, source: String = "apple-healthkit") async throws -> NativeHealthSyncRequest {
        let preview = try await loadPreview()
        return NativeHealthSyncRequest(
            sessionId: sessionId,
            profileId: profileId,
            source: source,
            deviceName: "iPhone + Apple Health",
            devices: ["Apple Health", "Apple Watch"],
            metrics: NativeHealthMetrics(
                heightCm: preview.heightCm,
                weightKg: preview.weightKg,
                bodyFat: preview.bodyFatPercentage,
                restingHeartRate: preview.restingHeartRate,
                stepCount: preview.stepCountToday,
                activeEnergyBurned: preview.activeEnergyToday
            ),
            workouts: preview.workouts
        )
    }

    private func latestQuantity(_ identifier: HKQuantityTypeIdentifier, unit: HKUnit) async throws -> Double? {
        guard let quantityType = HKObjectType.quantityType(forIdentifier: identifier) else {
            return nil
        }

        return try await withCheckedThrowingContinuation { continuation in
            let sort = NSSortDescriptor(key: HKSampleSortIdentifierEndDate, ascending: false)
            let query = HKSampleQuery(sampleType: quantityType, predicate: nil, limit: 1, sortDescriptors: [sort]) { _, samples, error in
                if let error {
                    continuation.resume(throwing: error)
                    return
                }
                guard let sample = samples?.first as? HKQuantitySample else {
                    continuation.resume(returning: nil)
                    return
                }
                continuation.resume(returning: sample.quantity.doubleValue(for: unit))
            }
            self.healthStore.execute(query)
        }
    }

    private func cumulativeQuantityToday(_ identifier: HKQuantityTypeIdentifier, unit: HKUnit) async throws -> Double? {
        guard let quantityType = HKObjectType.quantityType(forIdentifier: identifier) else {
            return nil
        }

        let startOfDay = Calendar.current.startOfDay(for: Date())
        let predicate = HKQuery.predicateForSamples(withStart: startOfDay, end: Date())

        return try await withCheckedThrowingContinuation { continuation in
            let query = HKStatisticsQuery(quantityType: quantityType, quantitySamplePredicate: predicate, options: .cumulativeSum) { _, result, error in
                if let error {
                    continuation.resume(throwing: error)
                    return
                }
                continuation.resume(returning: result?.sumQuantity()?.doubleValue(for: unit))
            }
            self.healthStore.execute(query)
        }
    }

    private func recentWorkouts(since startDate: Date, limit: Int = 20) async throws -> [NativeWorkoutPayload] {
        let predicate = HKQuery.predicateForSamples(withStart: startDate, end: Date())
        let sort = NSSortDescriptor(key: HKSampleSortIdentifierEndDate, ascending: false)

        return try await withCheckedThrowingContinuation { continuation in
            let query = HKSampleQuery(sampleType: HKObjectType.workoutType(), predicate: predicate, limit: limit, sortDescriptors: [sort]) { _, samples, error in
                if let error {
                    continuation.resume(throwing: error)
                    return
                }

                let workouts = (samples as? [HKWorkout] ?? []).map { workout in
                    NativeWorkoutPayload(
                        id: workout.uuid.uuidString,
                        externalId: workout.uuid.uuidString,
                        workoutType: workout.workoutActivityType.fitHubWorkoutType,
                        sportId: workout.workoutActivityType.fitHubSportId,
                        sportLabel: workout.workoutActivityType.fitHubSportLabel,
                        durationMinutes: max(1, Int(round(workout.duration / 60))),
                        distanceKm: workout.totalDistance?.doubleValue(for: HKUnit.meterUnit(with: .kilo)),
                        activeEnergyBurned: workout.totalEnergyBurned?.doubleValue(for: .kilocalorie()),
                        startedAt: self.isoFormatter.string(from: workout.startDate),
                        endedAt: self.isoFormatter.string(from: workout.endDate)
                    )
                }

                continuation.resume(returning: workouts)
            }
            self.healthStore.execute(query)
        }
    }
}

private extension HKWorkoutActivityType {
    var fitHubSportId: String {
        switch self {
        case .running:
            return "run"
        case .walking:
            return "outdoor-walk"
        case .hiking:
            return "hiking"
        case .cycling:
            return "outdoor-cycling"
        case .traditionalStrengthTraining, .functionalStrengthTraining:
            return "strength"
        case .highIntensityIntervalTraining:
            return "hiit"
        case .yoga:
            return "yoga"
        case .pilates:
            return "pilates"
        case .swimming:
            return "swim"
        case .rowing:
            return "rowing"
        case .elliptical:
            return "elliptical"
        case .stairClimbing:
            return "stairs"
        default:
            return "cardio-mix"
        }
    }

    var fitHubSportLabel: String {
        switch self {
        case .running:
            return "户外跑步"
        case .walking:
            return "户外行走"
        case .hiking:
            return "徒步"
        case .cycling:
            return "户外骑行"
        case .traditionalStrengthTraining, .functionalStrengthTraining:
            return "传统力量训练"
        case .highIntensityIntervalTraining:
            return "HIIT"
        case .yoga:
            return "瑜伽"
        case .pilates:
            return "普拉提"
        case .swimming:
            return "泳池游泳"
        case .rowing:
            return "划船机"
        case .elliptical:
            return "椭圆机"
        case .stairClimbing:
            return "爬楼梯"
        default:
            return "混合有氧"
        }
    }

    var fitHubWorkoutType: String {
        switch self {
        case .running:
            return "running"
        case .walking:
            return "walking"
        case .hiking:
            return "hiking"
        case .cycling:
            return "cycling"
        case .traditionalStrengthTraining:
            return "traditionalStrengthTraining"
        case .functionalStrengthTraining:
            return "functionalStrengthTraining"
        case .highIntensityIntervalTraining:
            return "highIntensityIntervalTraining"
        case .yoga:
            return "yoga"
        case .pilates:
            return "pilates"
        case .swimming:
            return "swimming"
        case .rowing:
            return "rowing"
        case .elliptical:
            return "elliptical"
        case .stairClimbing:
            return "stairClimbing"
        default:
            return "mixedCardio"
        }
    }
}
