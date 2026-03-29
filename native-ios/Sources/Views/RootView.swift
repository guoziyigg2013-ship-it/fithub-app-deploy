import SwiftUI

struct RootView: View {
    @EnvironmentObject private var store: AppStore

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 20) {
                    loginCard
                    if let profile = store.currentProfile {
                        profileCard(profile)
                        if profile.role == "enthusiast" {
                            syncCard
                        } else {
                            unsupportedRoleCard(profile)
                        }
                        if let preview = store.healthPreview, profile.role == "enthusiast" {
                            previewCard(preview)
                        }
                    }
                }
                .padding(20)
            }
            .background(Color(.systemGroupedBackground))
            .navigationTitle("FitHub 原生同步")
            .task {
                await store.bootstrapIfPossible()
            }
        }
    }

    private var loginCard: some View {
        VStack(alignment: .leading, spacing: 14) {
            Text("账户连接")
                .font(.headline)
            TextField("正式网址", text: $store.serverURL)
                .textInputAutocapitalization(.never)
                .keyboardType(.URL)
                .textFieldStyle(.roundedBorder)
            Picker("身份", selection: $store.selectedRole) {
                Text("健身爱好者").tag("enthusiast")
                Text("健身房").tag("gym")
                Text("教练").tag("coach")
            }
            .pickerStyle(.segmented)
            TextField("手机号", text: $store.phone)
                .keyboardType(.phonePad)
                .textFieldStyle(.roundedBorder)
            Button {
                Task {
                    do {
                        try await store.login()
                    } catch {
                        store.statusMessage = error.localizedDescription
                    }
                }
            } label: {
                Text(store.isBusy ? "连接中..." : "登录 FitHub")
                    .frame(maxWidth: .infinity)
            }
            .buttonStyle(.borderedProminent)

            Text(store.statusMessage)
                .font(.footnote)
                .foregroundStyle(.secondary)
        }
        .padding(18)
        .background(.background)
        .clipShape(RoundedRectangle(cornerRadius: 24, style: .continuous))
    }

    private func unsupportedRoleCard(_ profile: BootstrapResponse.Profile) -> some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("当前身份暂不支持健康同步")
                .font(.headline)
            Text("\(profile.name) 目前是 \(roleLabel(profile.role))，Apple Health / Apple Watch 同步仅对健身爱好者开放。")
                .font(.footnote)
                .foregroundStyle(.secondary)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(18)
        .background(.background)
        .clipShape(RoundedRectangle(cornerRadius: 24, style: .continuous))
    }

    private func profileCard(_ profile: BootstrapResponse.Profile) -> some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(profile.name)
                .font(.title3.weight(.semibold))
            Text(profile.locationLabel ?? "未同步地址")
                .font(.subheadline)
                .foregroundStyle(.secondary)
            HStack {
                Label(profile.healthSource ?? "未同步", systemImage: "heart.text.square")
                Spacer()
                Text(profile.deviceSyncedAt ?? "未同步")
            }
            .font(.footnote)
            if let devices = profile.connectedDevices, !devices.isEmpty {
                Text(devices.joined(separator: " · "))
                    .font(.footnote)
                    .foregroundStyle(.secondary)
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(18)
        .background(.background)
        .clipShape(RoundedRectangle(cornerRadius: 24, style: .continuous))
    }

    private var syncCard: some View {
        VStack(alignment: .leading, spacing: 14) {
            Text("Apple Health / Apple Watch")
                .font(.headline)
            Text("先读取 Apple Health，再把 Apple Watch 和健康数据同步回你的 FitHub 正式账户。")
                .font(.footnote)
                .foregroundStyle(.secondary)
            HStack(spacing: 12) {
                Button("读取预览") {
                    Task {
                        await store.refreshPreview()
                    }
                }
                .buttonStyle(.bordered)

                Button {
                    Task {
                        await store.syncAppleHealth()
                    }
                } label: {
                    Text(store.isBusy ? "同步中..." : "同步到 FitHub")
                        .frame(maxWidth: .infinity)
                }
                .buttonStyle(.borderedProminent)
            }
        }
        .padding(18)
        .background(.background)
        .clipShape(RoundedRectangle(cornerRadius: 24, style: .continuous))
    }

    private func previewCard(_ preview: HealthPreview) -> some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("本机健康预览")
                .font(.headline)
            VStack(alignment: .leading, spacing: 8) {
                previewLine("身高", preview.heightCm.map { "\($0) cm" } ?? "--")
                previewLine("体重", preview.weightKg.map { String(format: "%.1f kg", $0) } ?? "--")
                previewLine("体脂", preview.bodyFatPercentage.map { String(format: "%.1f%%", $0) } ?? "--")
                previewLine("静息心率", preview.restingHeartRate.map { "\($0) bpm" } ?? "--")
                previewLine("今日步数", preview.stepCountToday.map(String.init) ?? "--")
                previewLine("今日活跃卡路里", preview.activeEnergyToday.map { String(format: "%.0f kcal", $0) } ?? "--")
                previewLine("最近训练", "\(preview.workouts.count) 条")
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(18)
        .background(.background)
        .clipShape(RoundedRectangle(cornerRadius: 24, style: .continuous))
    }

    private func previewLine(_ title: String, _ value: String) -> some View {
        HStack {
            Text(title)
                .foregroundStyle(.secondary)
            Spacer()
            Text(value)
                .fontWeight(.medium)
        }
        .font(.subheadline)
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
