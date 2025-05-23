import Foundation

class AudioUploader {
    let onDevice = false
    
    func upload(fileURL: URL, completion: @escaping (Result<[Prediction], Error>) -> Void) {
        let serverAddress = Config.API_URL + (onDevice ? "/audio/features" : "/audio/uploadStream")
        
        DispatchQueue.global(qos: .background).async {
            do {
                let fileData = try Data(contentsOf: fileURL)
                
                guard let url = URL(string: serverAddress) else {
                    print("Error: Invalid Server URL")
                    return;
                }
                
                var request = URLRequest(url: url)
                request.httpMethod = "POST"
                request.setValue("audio/wave", forHTTPHeaderField: "Content-Type")
                request.httpBody = fileData
                
                let task = URLSession.shared.dataTask(with: request) { data, response, error in
                    if let error = error {
                        print(error)
                        return
                    }
                    
                    if let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode != 200 {
                        print("Server returned error: \(httpResponse.statusCode)")
                        return
                    }
                    
                    guard let data = data else {
                        print("Error: No data received from server")
                        return
                    }
                    
                    let decoder = JSONDecoder()
                    
                    if (self.onDevice) {
                        print((try? decoder.decode([Double].self, from:data)) ?? [0.0])
                        
                        DispatchQueue.main.async{
                            completion(
                                .success(
                                    predictUsingLocalModel(
                                        featuresArray: (try? decoder.decode([Double].self, from:data)) ?? [0.0]
                                    )
                                )
                            )
                        }
                    } else {
                        do {
                            let predictions = try decoder.decode([Prediction].self, from: data)
                            completion(.success(predictions))
                        } catch {
                            let decodingError = NSError(domain: "Uploader", code: 1003, userInfo: [NSLocalizedDescriptionKey: "Failed to decode predictions"])
                            completion(.failure(decodingError))
                        }
                    }
                }
                
                task.resume()
            } catch {
                print(error)
            }
        }
    }
}
