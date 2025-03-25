import SwiftUI
import AVFoundation

var recordingQueue = DispatchQueue(label:"recording")

struct ContentView: View {
    @ObservedObject var viewModel: ViewModel
    
    //Audio Utils
    var engine = AVAudioEngine()
    @State private var audioFile: AVAudioFile?
    
    @State private var isSheetPresent: Bool = true
    @State private var selectedDetent: PresentationDetent = .fraction(0.125)
    
    var body: some View {
        Spacer()
        Button(action: {
            startRecording(length:5);
        }) {
            ZStack {
                Circle()
                    .fill(Color(red: 0.48, green: 0.14, blue: 0.58))
                Image(systemName: "microphone.fill")
                    .resizable()
                    .aspectRatio(contentMode: .fit)
                    .frame(width: 60)
                    .foregroundStyle(Color.white)
            }
            .padding(75)
            .shadow(radius: 10)
        }.sheet(isPresented: $isSheetPresent, content: {
            NavigationStack {
                HStack {
                    NavigationLink(
                        destination: PredictionsView(viewModel: viewModel)
                    ) {
                        if (selectedDetent != .fraction(0.125)) {
                            Image(systemName: "figure.dance")
                                .resizable()
                                .scaledToFit()
                                .frame(width: 32, height: 32)
                                .foregroundStyle(Color(red: 0.48, green: 0.14, blue: 0.58))
                                .padding(18)
                        }
                    }
                    Spacer()
                }
                
                DancesView(viewModel: viewModel)
                    .presentationDetents(
                        [.fraction(0.125), .fraction(0.7), .fraction(1)],
                        selection: $selectedDetent
                    )
                    .presentationBackgroundInteraction(
                        .enabled(upThrough: .fraction(0.125))
                    )
                    .presentationDragIndicator(.visible)
                    .interactiveDismissDisabled(true)
            }
        })
        .padding()
        Spacer()
        Spacer()
        Spacer()
    }
    
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
                engine.stop()
                engine.reset()
                print("Recording stopped and saved to \(outputFileURL)")
                self.sendRecording(fileURL: outputFileURL)
            }
        }
        recordingQueue.async{record()}
    }
    
    private func sendRecording(fileURL: URL) {
        DispatchQueue.global(qos: .userInitiated).async {
            do {
                let fileData = try Data(contentsOf: fileURL)
                
                guard let url = URL(string: "http://192.168.178.95/upload/save") else {
                    print("Invalid server URL")
                    return
                }
                
                var request = URLRequest(url: url)
                request.httpMethod = "POST"
                
                
                //Multipart Data (courtesy of deepseek)
                
                let boundary = "Boundary-\(UUID().uuidString)"
                request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")
                
                var body = Data()
                
                body.append("--\(boundary)\r\n".data(using: .utf8)!)
                body.append("Content-Disposition: form-data; name=\"fileName\"\r\n\r\n".data(using: .utf8)!)
                body.append("recordedAudio.wav\r\n".data(using: .utf8)!)
                
                
                body.append("--\(boundary)\r\n".data(using: .utf8)!)
                body.append("Content-Disposition: form-data; name=\"file\"; filename=\"recordedAudio.wav\"\r\n".data(using: .utf8)!)
                body.append("Content-Type: audio/wav\r\n\r\n".data(using: .utf8)!)
                body.append(fileData)
                body.append("\r\n".data(using: .utf8)!)
                
                body.append("--\(boundary)--\r\n".data(using: .utf8)!)
                
                request.httpBody = body
                
                
                let task = URLSession.shared.dataTask(with: request) { data, response, error in
                    if let error = error {
                        print("Upload error: \(error.localizedDescription)")
                        return
                    }
                    
                    if let httpResponse = response as? HTTPURLResponse {
                        print("Response Code: \(httpResponse.statusCode)")
                        
                        if let data = data, let responseString = String(data: data, encoding: .utf8) {
                            print("Response: \(responseString)")
                        }
                    }
                }
                
                task.resume()
                
            } catch {
                print("Error reading file or sending to server: \(error)")
            }
        }
    }
}

#Preview {
    let model: Model = Model()
    let viewModel: ViewModel = ViewModel(model: model)
    
    return ContentView(viewModel: viewModel)
}
