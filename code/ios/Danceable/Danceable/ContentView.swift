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
            Button(action: { recordAndPredict() }) {
                RecordButtonView(isWatch: false, audioController: audioController)
            }
            .disabled(audioController.isRecording)
            .sheet(isPresented: $isSheetPresent) {
                PredictionSheetView(viewModel: viewModel, selectedDetent: $selectedDetent)
            }
            Spacer()
            Spacer()
            Spacer()
            .toolbar {
                ToolbarItem(placement: .topBarLeading) {
                    DancesNavigationLinkView(viewModel: viewModel, isSheetPresent: $isSheetPresent, hasPredicted: $hasPredicted)
                }
            }
        }
        .task { loadDancesAsync() }
    }
    
    private func recordAndPredict() {
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
    }
    
    private func loadDancesAsync() {
        queue.async(execute: {
            let dances = fetchDances()
            
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
