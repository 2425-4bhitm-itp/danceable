import Foundation

let DANCE_URL = Config.API_URL + "/dances"

func fetchDances() async -> [Dance] {
    guard let url = URL(string: DANCE_URL) else {
        print("Invalid URL: \(DANCE_URL)")
        return []
    }

    do {
        let (data, _) = try await URLSession.shared.data(from: url)
        let decoder = JSONDecoder()
        let dances = try decoder.decode([Dance].self, from: data)
        return dances
    } catch {
        print("Failed to fetch or decode dances: \(error)")
        return []
    }
}
