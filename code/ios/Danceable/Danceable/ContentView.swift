import SwiftUI
import AVFoundation

let MIN_SHEET_FRACTION: CGFloat = 0.175
let MAX_SHEET_FRACTION: CGFloat = 0.7

struct ContentView: View {
    let queue = DispatchQueue(label: "at.htl.leonding")
    
    var viewModel: ViewModel
    
    @StateObject private var audioController = AudioController()
    
    @State private var isSheetPresent = false
    
    @State private var selectedDetent: PresentationDetent = .fraction(MIN_SHEET_FRACTION)
    
    @State private var hasPredicted = false
    
    var body: some View {
        NavigationStack {
            Spacer()
            Button(action: {
                audioController.recordAndUploadAudio(duration: 3.0) { result in
                    switch result {
                    case .success(let predictions):
                        print("Received predictions: \(predictions)")
                        viewModel.predictions = predictions
                        selectedDetent = .fraction(MAX_SHEET_FRACTION)
                        isSheetPresent = true
                        hasPredicted = true
                    case .failure(let error):
                        print("Error: \(error.localizedDescription)")
                    }
                }
            }) {
                RecordButtonView(isWatch: false, audioController: audioController)
            }
            .disabled(audioController.isRecording)
            .sheet(isPresented: $isSheetPresent) {
                PredictionsView(viewModel: viewModel)
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
                            isSheetPresent = hasPredicted
                        }
                    }) {
                        Image(systemName: "list.bullet.circle.fill")
                            .resizable()
                            .frame(width: 30, height: 30)
                    }
                }
            }
        }
        .task { loadDancesAsync() }
    }
    
    private func loadDancesAsync() {
        queue.async(execute: {
            let dances = loadDances()
            
            DispatchQueue.main.async(execute: {
                viewModel.model.dances = dances
            })
        })
    }
}

#Preview {
    let model: Model = Model()
    let viewModel: ViewModel = ViewModel(model: model)
    
    return ContentView(viewModel: viewModel)
}
