import Foundation
import AVFoundation

class AudioRecorder: ObservableObject {
    let queue = DispatchQueue(label: "at.htl.leonding")
    
    var engine = AVAudioEngine()
    var audioFile: AVAudioFile?
    
    func startRecording(length:Double) {
        let input = engine.inputNode
        
        let format = input.outputFormat(forBus: 0)
        print("Output format: \(format)")
        
        // find Documents Directory in current Container and set the URL
        let documentsDirectory = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
        let outputFileURL = documentsDirectory.appendingPathComponent("recordedAudio.wav")
        
        // Define WAV format settings (courtesy of DeepSeek)
        let wavSettings: [String: Any] = [
            AVFormatIDKey: kAudioFormatLinearPCM, // Linear PCM for WAV
            AVSampleRateKey: format.sampleRate,
            AVNumberOfChannelsKey: format.channelCount,
            AVLinearPCMBitDepthKey: 16, // 16-bit depth
            AVLinearPCMIsBigEndianKey: false, // Little-endian
            AVLinearPCMIsFloatKey: false, // Integer format
            AVLinearPCMIsNonInterleaved: false // Interleaved
        ]
        
        
        func record(){
            do {
                audioFile = try AVAudioFile(forWriting: outputFileURL, settings: wavSettings)
            } catch {
                print("Error creating audio file: \(error)")
                return
            }
            
            // installs a Tap to capture audio Stream until engine is stopped
            input.installTap(onBus: 0, bufferSize: 4096, format: format) { (buffer, when) in
                
                do {
                    try self.audioFile?.write(from: buffer)
                } catch {
                    print("Error writing to audio file: \(error)")
                }
            }
            
            // Start engine
            do {
                try engine.start()
            } catch {
                print("Error starting audio engine: \(error)")
                return
            }
            
            // Stop recording after x seconds
            DispatchQueue.main.asyncAfter(deadline: .now() + length) {
                self.engine.stop()
                self.engine.reset()
                print("Recording stopped and saved to \(outputFileURL)")
                self.saveRecording(fileURL: outputFileURL)
            }
        }
        recordingQueue.async{record()}
    }
    
    private func saveRecording(fileURL: URL) {
        DispatchQueue.global(qos: .background).async {
            do {
                
                let fileData = try Data(contentsOf: fileURL)
                print (fileData)
                
                guard let url = URL(string: "http://<YOUR_SERVER_IP>:8080/uploadStream") else {
                    print("Invalid server URL")
                    return
                }
                
                var request = URLRequest(url: url)
                request.httpMethod = "POST"
                
                request.setValue("audio/wav", forHTTPHeaderField: "Content-Type")
                
                request.httpBody = fileData
                
                
                let task = URLSession.shared.dataTask(with: request) {data, response, error in
                    if let httpResponse = response as? HTTPURLResponse {
                        print("Server response status code: \(httpResponse.statusCode)")
                    }
                }
                
                task.resume()
                
            } catch {
                print("Error reading file or sending to server: \(error)")
            }
        }
    }
}
