import Foundation

class AudioUploader {
    func upload(fileURL: URL, completion: @escaping (Result<[Prediction], Error>) -> Void) {
        DispatchQueue.global(qos: .background).async {
            do {
                let fileData = try Data(contentsOf: fileURL)
                let serverAddress = "http://localhost:8080/audio/uploadStream"
                
                guard let url = URL(string: serverAddress) else {
                    let error = NSError(domain: "Uploader", code: 1001, userInfo: [NSLocalizedDescriptionKey: "Invalid server URL"])
                    completion(.failure(error))
                    return
                }

                var request = URLRequest(url: url)
                request.httpMethod = "POST"
                request.setValue("audio/wave", forHTTPHeaderField: "Content-Type")
                request.httpBody = fileData

                let task = URLSession.shared.dataTask(with: request) { data, response, error in
                    if let error = error {
                        completion(.failure(error))
                        return
                    }

                    
                    if let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode != 200 {
                        let statusError = NSError(domain: "Uploader", code: httpResponse.statusCode, userInfo: [NSLocalizedDescriptionKey: "Server returned an error: \(httpResponse.statusCode)"])
                        completion(.failure(statusError))
                        return
                    }

                    
                    guard let data = data else {
                        let error = NSError(domain: "Uploader", code: 1002, userInfo: [NSLocalizedDescriptionKey: "No data received from server"])
                        completion(.failure(error))
                        return
                    }

                    
                    let decoder = JSONDecoder()
                    do {
                        let predictions = try decoder.decode([Prediction].self, from: data)
                        completion(.success(predictions))
                    } catch {
                        let decodingError = NSError(domain: "Uploader", code: 1003, userInfo: [NSLocalizedDescriptionKey: "Failed to decode predictions"])
                        completion(.failure(decodingError))
                    }
                }

                task.resume()
            } catch {
                completion(.failure(error))
            }
        }
    }
}
