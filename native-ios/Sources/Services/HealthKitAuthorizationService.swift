import Foundation
import HealthKit

enum HealthKitAuthorizationError: LocalizedError {
    case unavailable
    case denied

    var errorDescription: String? {
        switch self {
        case .unavailable:
            return "当前设备不支持 HealthKit。"
        case .denied:
            return "你还没有允许 FitHub 读取健康数据。"
        }
    }
}

final class HealthKitAuthorizationService {
    let healthStore = HKHealthStore()

    func requestReadAccess() async throws {
        guard HKHealthStore.isHealthDataAvailable() else {
            throw HealthKitAuthorizationError.unavailable
        }

        let readTypes: Set<HKObjectType> = [
            HKObjectType.workoutType(),
            HKObjectType.quantityType(forIdentifier: .height),
            HKObjectType.quantityType(forIdentifier: .bodyMass),
            HKObjectType.quantityType(forIdentifier: .bodyFatPercentage),
            HKObjectType.quantityType(forIdentifier: .restingHeartRate),
            HKObjectType.quantityType(forIdentifier: .stepCount),
            HKObjectType.quantityType(forIdentifier: .activeEnergyBurned),
        ]
        .compactMap { $0 }

        try await withCheckedThrowingContinuation { continuation in
            healthStore.requestAuthorization(toShare: [], read: readTypes) { success, error in
                if let error {
                    continuation.resume(throwing: error)
                    return
                }
                if success {
                    continuation.resume()
                } else {
                    continuation.resume(throwing: HealthKitAuthorizationError.denied)
                }
            }
        }
    }
}
