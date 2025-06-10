import Foundation

class AudioUploader {    
    func classifyOnDevice(fileURL: URL) async throws -> [Prediction] {
        let features = try await features(fileURL: fileURL)
        
        return predictUsingLocalModel(featuresArray: features)
    }
    
    func classify(fileURL: URL) async throws -> [Prediction] {
        let apiAddress = Config.API_URL + "/audio/uploadStream"
        
        guard let url = URL(string: apiAddress) else {
            throw URLError(.badURL)
        }
        
        let fileData = try Data(contentsOf: fileURL)
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("audio/wave", forHTTPHeaderField: "Content-Type")
        request.httpBody = fileData

        let (data, response) = try await URLSession.shared.data(for: request)

        guard let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode == 200 else {
            throw NSError(domain: "Uploader", code: 1001, userInfo: [NSLocalizedDescriptionKey: "Server returned an error"])
        }

        return try JSONDecoder().decode([Prediction].self, from: data)
    }
    
    func features(fileURL: URL) async throws -> [Double] {
        let apiAddress = Config.API_URL + "/audio/features"
        
        guard let url = URL(string: apiAddress) else {
            throw URLError(.badURL)
        }
        
        let fileData = try Data(contentsOf: fileURL)
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("audio/wave", forHTTPHeaderField: "Content-Type")
        request.httpBody = fileData

        let (data, response) = try await URLSession.shared.data(for: request)

        guard let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode == 200 else {
            throw NSError(domain: "Uploader", code: 1001, userInfo: [NSLocalizedDescriptionKey: "Server returned an error"])
        }

        return try decoder.decode([Double].self, from: data)
    }
}
