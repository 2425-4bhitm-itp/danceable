import SwiftUI
import AVFoundation

var recordingQueue = DispatchQueue(label: "recording")

let MIN_SHEET_FRACTION: CGFloat = 0.175
let MAX_SHEET_FRACTION: CGFloat = 0.7

struct ContentView: View {
    @ObservedObject var viewModel: ViewModel
    
    @StateObject private var audioController = AudioController()
    
    let queue = DispatchQueue(label: "at.htl.leonding")
    
    @State var showDancesView = false
    
    @State private var isSheetPresent: Bool = false
    
    @State private var selectedDetent: PresentationDetent = .fraction(MIN_SHEET_FRACTION)
    
    @State private var areDancesDisplayed: Bool = false
    
    var body: some View {
        NavigationStack {
            Spacer()
            Button(action: {
                audioController.recordAndUploadAudio(duration: 5.0) { result in
                    switch result {
                    case .success(let predictions):
                        print("Received predictions: \(predictions)")
                        viewModel.predictions = predictions
                        selectedDetent = .fraction(MAX_SHEET_FRACTION)
                        isSheetPresent = true
                    case .failure(let error):
                        print("Error: \(error.localizedDescription)")
                    }
                }
            }) {
                ZStack {
                    Circle()
                        .fill(Color(red: 0.48, green: 0.14, blue: 0.58))
                    if (!audioController.isRecording) {
                        Image(systemName: "microphone.fill")
                            .resizable()
                            .aspectRatio(contentMode: .fit)
                            .frame(width: 60)
                            .foregroundStyle(Color.white)
                    } else {
                        RecordingAnimationView(soundLevels: audioController.soundLevels)
                    }
                    
                }
                .padding(75)
                .shadow(radius: 10)
            }
            .disabled(audioController.isRecording)
            .onAppear() {
                isSheetPresent = viewModel.predictions.count != 0
            }
            .onReceive(audioController.$soundLevels) { levels in
                print("sound levels: \(levels)")
            }
            .sheet(isPresented: $isSheetPresent) {
                NavigationView {
                    PredictionsView(viewModel: viewModel)
                }
                .presentationDetents(
                    [.fraction(MIN_SHEET_FRACTION), .fraction(MAX_SHEET_FRACTION)],
                    selection: $selectedDetent
                )
                .presentationBackgroundInteraction(
                    .enabled(upThrough: .fraction(MAX_SHEET_FRACTION))
                )
                .presentationDragIndicator(.visible)
                .interactiveDismissDisabled(true)
            }
            Spacer()
            Spacer()
            Spacer()
            .toolbar {
                ToolbarItem(placement: .topBarLeading) {
                    NavigationLink(destination: {
                        Text("Avaliable Dances").font(.headline)
                        DancesView(viewModel: viewModel)
                        .onAppear {
                            isSheetPresent = false
                        }.onDisappear {
                            isSheetPresent = true
                        }
                    }) {
                        Image(systemName: "list.bullet.circle.fill")
                            .resizable()
                            .frame(width: 30, height: 30)
                    }
                }
            }
        }
        .task {
            queue.async(execute: {
                let dances = loadDances()
                
                DispatchQueue.main.async(execute: {
                    viewModel.model.dances = dances
                })
            })
        }
    }
}

#Preview {
    let model: Model = Model()
    let viewModel: ViewModel = ViewModel(model: model)
    
    return ContentView(viewModel: viewModel)
}
