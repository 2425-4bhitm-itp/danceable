import SwiftUI
import AVFoundation

var recordingQueue = DispatchQueue(label: "recording")

struct ContentView: View {
    @ObservedObject var viewModel: ViewModel
    
    let queue = DispatchQueue(label: "at.htl.leonding")
    
    @State var showDancesView = false
    
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
            VStack {
                /*if (selectedDetent != .fraction(0.125)) {
                    NavigationStack {
                        VStack {
                            NavigationLink(destination: DancesView(viewModel: viewModel)) {
                                Image(systemName: "figure.dance")
                                    .resizable()
                                    .scaledToFit()
                                    .frame(width: 32, height: 32)
                                    .foregroundStyle(Color(red: 0.48, green: 0.14, blue: 0.58))
                                    .padding(18)
                            }
                            Spacer()
                        }
                    }
                }*/
                
                PredictionsView(viewModel: viewModel)
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
        .toolbar {
            ToolbarItem(placement: .topBarLeading) {
                Image(systemName: "figure.dance")
                    .resizable()
                    .scaledToFit()
                    .frame(width: 32, height: 32)
                    .foregroundStyle(Color(red: 0.48, green: 0.14, blue: 0.58))
                    .padding(18)
            }
        }
        .padding()
        Spacer()
        Spacer()
        .task {
            queue.async(execute: {
                let dances = loadDances()
                
                DispatchQueue.main.async(execute: {
                    viewModel.model.dances = dances
                })
            })
        }
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
            }
        }
        recordingQueue.async{record()}
    }
}

#Preview {
    let model: Model = Model()
    let viewModel: ViewModel = ViewModel(model: model)
    
    return ContentView(viewModel: viewModel)
}
