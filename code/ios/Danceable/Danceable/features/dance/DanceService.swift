import Foundation

let DANCE_URL = Config.API_URL + "/dances"

func fetchDances() async throws -> [Dance] {
    guard let url = URL(string: DANCE_URL) else {
        throw URLError(.badURL)
    }

    let config = URLSessionConfiguration.default
    config.timeoutIntervalForRequest = 2

    let session = URLSession(configuration: config)

    let (data, _) = try await session.data(from: url)
    let decoder = JSONDecoder()

    return try decoder.decode([Dance].self, from: data)
}
