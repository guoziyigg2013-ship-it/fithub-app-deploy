import Foundation

struct BootstrapResponse: Decodable {
    struct SessionData: Decodable {
        let id: String
        let selectedRole: String
        let currentActorProfileId: String?
    }

    struct Profile: Decodable, Identifiable {
        let id: String
        let role: String
        let name: String
        let locationLabel: String?
        let connectedDevices: [String]?
        let healthSource: String?
        let deviceSyncedAt: String?
    }

    let session: SessionData
    let profiles: [Profile]
}

struct LoginRequest: Encodable {
    let sessionId: String
    let role: String
    let phone: String
}

struct NativeHealthSyncRequest: Encodable {
    let sessionId: String
    let profileId: String
    let source: String
    let deviceName: String
    let devices: [String]
    let metrics: NativeHealthMetrics
    let workouts: [NativeWorkoutPayload]
}

struct NativeHealthMetrics: Encodable {
    let heightCm: Int?
    let weightKg: Double?
    let bodyFat: Double?
    let restingHeartRate: Int?
    let stepCount: Int?
    let activeEnergyBurned: Double?
}

struct NativeWorkoutPayload: Encodable, Identifiable {
    let id: String
    let externalId: String
    let workoutType: String
    let sportId: String
    let sportLabel: String
    let durationMinutes: Int
    let distanceKm: Double?
    let activeEnergyBurned: Double?
    let startedAt: String
    let endedAt: String
}

struct NativeSyncSummary: Decodable {
    let source: String
    let importedWorkoutCount: Int
    let connectedDevices: [String]
    let syncedAt: String
}

struct NativeSyncResponse: Decodable {
    let session: BootstrapResponse.SessionData
    let profiles: [BootstrapResponse.Profile]
    let nativeSyncSummary: NativeSyncSummary?
}
