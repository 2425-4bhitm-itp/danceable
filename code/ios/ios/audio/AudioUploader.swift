import Foundation

class AudioUploader {
    let onDevice = true;
    
    func upload(fileURL: URL) {
        var serverAddress = "";
        
        if(onDevice){
            //replace address here
            serverAddress = Config.API_URL + "/audio/features"
        }else{
            serverAddress = Config.API_URL + "/audio/uploadStream"
        }
        
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
                        print("Error:  No data received from server")
                        return
                    }
                    
                    DispatchQueue.main.async{
                        predict(data:data, onDevice: true)
                    }
                }
                
                task.resume()
            } catch {
                print(error)
            }
        }
        
    }
}
