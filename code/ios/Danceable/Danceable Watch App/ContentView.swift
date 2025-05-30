import SwiftUI
import AVFoundation

let MIN_SHEET_FRACTION: CGFloat = 0.175
let MAX_SHEET_FRACTION: CGFloat = 0.7

struct ContentView: View {
    var viewModel: ViewModel
    
    var audioController = AudioController()
    
    @State private var isSheetPresent = false
    
    @State private var selectedDetent: PresentationDetent = .fraction(MIN_SHEET_FRACTION)
    
    @State private var hasPredicted = false
    
    var body: some View {
        NavigationStack {
            Spacer()
            Button(action: {
                Task {
                    await recordAndClassify()
                }
            }) {
                RecordButtonView(audioController: audioController)
            }
            .buttonStyle(PlainButtonStyle())
            .disabled(audioController.isRecording)
            .sheet(isPresented: $isSheetPresent) {
                PredictionSheetView(viewModel: viewModel, selectedDetent: $selectedDetent)
            }
            Spacer()
            Spacer()
            Spacer()
        }
        .task { await viewModel.updateDances() }
    }
    
    private func recordAndClassify() async {
        do {
            let predictions = try await audioController.recordAndClassify(duration: 3.0)
            
            await MainActor.run {
                viewModel.predictions = predictions
                selectedDetent = .fraction(MAX_SHEET_FRACTION)
                isSheetPresent = true
                hasPredicted = true
            }
            
        } catch {
            print("Failed to record and classify audio: \(error.localizedDescription)")
            
            await MainActor.run {
                isSheetPresent = false
                hasPredicted = false
            }
        }
    }

}

#Preview {
    let model: Model = Model()
    let viewModel: ViewModel = ViewModel(model: model)
    
    return ContentView(viewModel: viewModel)
}
