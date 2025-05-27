import SwiftUI

let MIN_SHEET_FRACTION: CGFloat = 0.175
let MAX_SHEET_FRACTION: CGFloat = 0.7


struct ContentView: View {
    @ObservedObject var viewModel: ViewModel
    
    @StateObject private var audioController = AudioController()
    
    let queue = DispatchQueue(label: "at.htl.leonding")
    
    @State private var isSheetPresent = false
    
    @State private var selectedDetent: PresentationDetent = .fraction(MIN_SHEET_FRACTION)
    
    @State private var hasPredicted = false
    
    var body: some View {
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
            RecordButtonView(audioController: audioController)
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
    }
}

#Preview {
    
}
