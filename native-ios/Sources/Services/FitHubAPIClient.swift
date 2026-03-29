import Foundation

enum FitHubAPIError: LocalizedError {
    case invalidBaseURL
    case server(String)
    case badResponse

    var errorDescription: String? {
        switch self {
        case .invalidBaseURL:
            return "服务器地址无效。"
        case let .server(message):
            return message
        case .badResponse:
            return "服务器返回了无法识别的数据。"
        }
    }
}

final class FitHubAPIClient {
    private let baseURLString: String
    private let decoder = JSONDecoder()
    private let encoder = JSONEncoder()

    init(baseURLString: String) {
        self.baseURLString = baseURLString.trimmingCharacters(in: .whitespacesAndNewlines)
    }

    func bootstrap(sessionId: String) async throws -> BootstrapResponse {
        guard let url = makeURL(path: "/bootstrap", queryItems: [URLQueryItem(name: "session_id", value: sessionId)]) else {
            throw FitHubAPIError.invalidBaseURL
        }

        let (data, response) = try await URLSession.shared.data(from: url)
        guard let http = response as? HTTPURLResponse, (200 ..< 300).contains(http.statusCode) else {
            throw try parseServerError(data: data)
        }
        return try decoder.decode(BootstrapResponse.self, from: data)
    }

    func login(sessionId: String, role: String, phone: String) async throws -> BootstrapResponse {
        let payload = LoginRequest(sessionId: sessionId, role: role, phone: phone)
        return try await send(path: "/auth/login", payload: payload, responseType: BootstrapResponse.self)
    }

    func syncHealth(_ payload: NativeHealthSyncRequest) async throws -> NativeSyncResponse {
        return try await send(path: "/health/native-sync", payload: payload, responseType: NativeSyncResponse.self)
    }

    private func send<T: Encodable, U: Decodable>(path: String, payload: T, responseType: U.Type) async throws -> U {
        guard let url = makeURL(path: path) else {
            throw FitHubAPIError.invalidBaseURL
        }

        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try encoder.encode(payload)

        let (data, response) = try await URLSession.shared.data(for: request)
        guard let http = response as? HTTPURLResponse else {
            throw FitHubAPIError.badResponse
        }
        guard (200 ..< 300).contains(http.statusCode) else {
            throw try parseServerError(data: data)
        }
        return try decoder.decode(responseType, from: data)
    }

    private func parseServerError(data: Data) throws -> Error {
        if
            let object = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
            let message = object["error"] as? String,
            !message.isEmpty
        {
            return FitHubAPIError.server(message)
        }
        return FitHubAPIError.badResponse
    }

    private func makeURL(path: String, queryItems: [URLQueryItem] = []) -> URL? {
        let cleanBase = baseURLString.hasSuffix("/") ? String(baseURLString.dropLast()) : baseURLString
        guard var components = URLComponents(string: cleanBase) else {
            return nil
        }

        let prefix = components.path.hasSuffix("/fitness-app-prototype") ? "/fitness-app-prototype/api" : "/api"
        components.path = prefix + path
        components.queryItems = queryItems.isEmpty ? nil : queryItems
        return components.url
    }
}
