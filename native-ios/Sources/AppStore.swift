import SwiftUI

@MainActor
final class AppStore: ObservableObject {
    @Published var serverURL: String
    @Published var phone: String
    @Published var selectedRole: String
    @Published var bootstrap: BootstrapResponse?
    @Published var healthPreview: HealthPreview?
    @Published var statusMessage: String = "连接 Apple Health 后即可把真实训练同步到 FitHub。"
    @Published var isBusy = false

    private let defaults = UserDefaults.standard
    private let serverURLKey = "fithub.native.serverURL"
    private let phoneKey = "fithub.native.phone"
    private let roleKey = "fithub.native.role"
    private let sessionIdKey = "fithub.native.sessionId"
    private let authorizationService = HealthKitAuthorizationService()
    private let sessionId: String

    init() {
        let storedSession = defaults.string(forKey: sessionIdKey) ?? UUID().uuidString
        defaults.set(storedSession, forKey: sessionIdKey)
        sessionId = storedSession
        serverURL = defaults.string(forKey: serverURLKey) ?? "https://fithub-app-1btg.onrender.com"
        phone = defaults.string(forKey: phoneKey) ?? ""
        selectedRole = defaults.string(forKey: roleKey) ?? "enthusiast"
    }

    var apiClient: FitHubAPIClient {
        FitHubAPIClient(baseURLString: serverURL)
    }

    var syncService: HealthKitSyncService {
        HealthKitSyncService(healthStore: authorizationService.healthStore)
    }

    var currentProfile: BootstrapResponse.Profile? {
        guard let bootstrap else { return nil }
        if let currentId = bootstrap.session.currentActorProfileId {
            return bootstrap.profiles.first(where: { $0.id == currentId })
        }
        return bootstrap.profiles.first(where: { $0.role == selectedRole }) ?? bootstrap.profiles.first
    }

    func bootstrapIfPossible() async {
        persistForm()
        do {
            let response = try await apiClient.bootstrap(sessionId: sessionId)
            bootstrap = response
            if currentProfile == nil, !phone.isEmpty {
                try await login()
            }
        } catch {
            statusMessage = error.localizedDescription
        }
    }

    func login() async throws {
        persistForm()
        isBusy = true
        defer { isBusy = false }
        let response = try await apiClient.login(sessionId: sessionId, role: selectedRole, phone: phone)
        bootstrap = response
        statusMessage = "已登录 \(currentProfile?.name ?? "FitHub")，可以开始同步真实健康数据。"
    }

    func refreshPreview() async {
        do {
            try await authorizationService.requestReadAccess()
            healthPreview = try await syncService.loadPreview()
            statusMessage = "已读取 Apple Health，可点击“同步到 FitHub”写入正式账户。"
        } catch {
            statusMessage = error.localizedDescription
        }
    }

    func syncAppleHealth() async {
        guard let profile = currentProfile else {
            statusMessage = "请先用手机号登录 FitHub 账户。"
            return
        }

        isBusy = true
        defer { isBusy = false }

        do {
            try await authorizationService.requestReadAccess()
            let request = try await syncService.makeSyncRequest(sessionId: sessionId, profileId: profile.id)
            healthPreview = try await syncService.loadPreview()
            let response = try await apiClient.syncHealth(request)
            bootstrap = BootstrapResponse(session: response.session, profiles: response.profiles)
            let imported = response.nativeSyncSummary?.importedWorkoutCount ?? 0
            statusMessage = "同步完成，已导入 \(imported) 条训练记录。"
        } catch {
            statusMessage = error.localizedDescription
        }
    }

    private func persistForm() {
        defaults.set(serverURL, forKey: serverURLKey)
        defaults.set(phone, forKey: phoneKey)
        defaults.set(selectedRole, forKey: roleKey)
    }
}
