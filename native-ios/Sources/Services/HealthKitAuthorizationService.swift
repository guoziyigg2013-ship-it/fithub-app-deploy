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

    private var readTypes: Set<HKObjectType> {
        [
            HKObjectType.workoutType(),
            HKObjectType.quantityType(forIdentifier: .height),
            HKObjectType.quantityType(forIdentifier: .bodyMass),
            HKObjectType.quantityType(forIdentifier: .bodyFatPercentage),
            HKObjectType.quantityType(forIdentifier: .restingHeartRate),
            HKObjectType.quantityType(forIdentifier: .stepCount),
            HKObjectType.quantityType(forIdentifier: .activeEnergyBurned),
        ]
        .compactMap { $0 }
    }

    func permissionSummary() async -> String {
        guard HKHealthStore.isHealthDataAvailable() else {
            return "当前 iPhone 不支持 Apple Health。"
        }

        return await withCheckedContinuation { continuation in
            healthStore.getRequestStatusForAuthorization(toShare: [], read: readTypes) { status, error in
                if let error {
                    continuation.resume(returning: error.localizedDescription)
                    return
                }

                let message: String
                switch status {
                case .shouldRequest:
                    message = "还没有向系统申请 Apple Health 读取权限。"
                case .unnecessary:
                    message = "Apple Health 读取权限已准备好，可以直接读取预览。"
                case .unknown:
                    message = "Apple Health 权限状态未知，请在真机上检查。"
                @unknown default:
                    message = "Apple Health 权限状态未知，请升级系统后再试。"
                }
                continuation.resume(returning: message)
            }
        }
    }

    func requestReadAccess() async throws {
        guard HKHealthStore.isHealthDataAvailable() else {
            throw HealthKitAuthorizationError.unavailable
        }

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
