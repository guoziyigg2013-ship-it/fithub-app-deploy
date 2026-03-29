import SwiftUI

@MainActor
final class AppStore: ObservableObject {
    @Published var serverURL: String
    @Published var phone: String
    @Published var selectedRole: String
    @Published var bootstrap: BootstrapResponse?
    @Published var healthPreview: HealthPreview?
    @Published var statusMessage: String = "连接 Apple Health 后即可把真实训练同步到 FitHub。"
    @Published var healthPermissionStatus: String = "正在检查 Apple Health 权限..."
    @Published var lastSyncSummary: String = "还没有把真实设备数据同步到 FitHub。"
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

    var canLogin: Bool {
        !phone.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty && !isBusy
    }

    var canSyncHealth: Bool {
        guard let profile = currentProfile else { return false }
        return profile.role == "enthusiast" && !isBusy
    }

    var serverHostLabel: String {
        guard let host = URL(string: serverURL)?.host, !host.isEmpty else {
            return serverURL
        }
        return host
    }

    var connectionSummary: String {
        guard let profile = currentProfile else {
            return "还没有连接到 FitHub 账户。"
        }
        return "当前已连接 \(profile.name)，身份为 \(roleLabel(profile.role))。"
    }

    var selectedRoleLabel: String {
        roleLabel(selectedRole)
    }

    var healthPermissionBadge: String {
        if healthPermissionStatus.contains("准备好") {
            return "权限已就绪"
        }
        if healthPermissionStatus.contains("还没有") {
            return "待授权"
        }
        if healthPermissionStatus.contains("不支持") {
            return "当前设备不支持"
        }
        return "待检查"
    }

    func prepareForLaunch() async {
        async let permission = authorizationService.permissionSummary()
        await bootstrapIfPossible()
        healthPermissionStatus = await permission
        refreshLastSyncSummary()
    }

    func bootstrapIfPossible() async {
        persistForm()
        do {
            let response = try await apiClient.bootstrap(sessionId: sessionId)
            bootstrap = response
            if currentProfile == nil, !phone.isEmpty {
                try await login()
            }
            refreshLastSyncSummary()
        } catch {
            statusMessage = error.localizedDescription
        }
    }

    func refreshAccount() async {
        async let permission = authorizationService.permissionSummary()
        await bootstrapIfPossible()
        healthPermissionStatus = await permission
        if currentProfile != nil {
            statusMessage = connectionSummary
        }
        refreshLastSyncSummary()
    }

    func refreshHealthPermissionStatus() async {
        healthPermissionStatus = await authorizationService.permissionSummary()
    }

    func login() async throws {
        guard !phone.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else {
            throw FitHubAPIError.server("请先填写手机号。")
        }
        persistForm()
        isBusy = true
        defer { isBusy = false }
        let response = try await apiClient.login(sessionId: sessionId, role: selectedRole, phone: phone)
        bootstrap = response
        refreshLastSyncSummary()
        statusMessage = "已登录 \(currentProfile?.name ?? "FitHub")，可以开始同步真实健康数据。"
    }

    func refreshPreview() async {
        isBusy = true
        defer { isBusy = false }
        do {
            try await authorizationService.requestReadAccess()
            healthPermissionStatus = await authorizationService.permissionSummary()
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
        guard profile.role == "enthusiast" else {
            statusMessage = "当前只有健身爱好者身份支持同步 Apple Health。"
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
            healthPermissionStatus = await authorizationService.permissionSummary()
            lastSyncSummary = "刚刚同步了 \(imported) 条训练记录。"
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

    private func refreshLastSyncSummary() {
        guard let profile = currentProfile else {
            lastSyncSummary = "还没有把真实设备数据同步到 FitHub。"
            return
        }

        if let syncedAt = profile.deviceSyncedAt, !syncedAt.isEmpty {
            let source = profile.healthSource ?? "Apple Health"
            lastSyncSummary = "\(source) 最近一次同步时间：\(syncedAt)"
            return
        }

        if let devices = profile.connectedDevices, !devices.isEmpty {
            lastSyncSummary = "已连接 \(devices.joined(separator: " · "))，还没有完成首次同步。"
            return
        }

        lastSyncSummary = "当前账户还没有设备同步记录。"
    }

    private func roleLabel(_ role: String) -> String {
        switch role {
        case "gym":
            return "健身房"
        case "coach":
            return "健身教练"
        default:
            return "健身爱好者"
        }
    }
}
