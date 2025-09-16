import SwiftUI
import AVFoundation

let MIN_SHEET_FRACTION: CGFloat = 0.175
let MAX_SHEET_FRACTION: CGFloat = 0.7

struct ContentView: View {
    var viewModel: ViewModel
    
    var strategy: RecordButtonStrategy
    
    var audioController: AudioController
    
    var haptics: HapticsStrategy
    
    var orientation: OrientationStrategy
    
    init(viewModel: ViewModel) {
        self.viewModel = viewModel
        
        self.haptics = WatchHapticsStrategy()
        self.audioController = AudioController(numberOfSoundLevels: 7, hapticsStrategy: self.haptics)
        self.strategy = WatchRecordButtonStrategy()
        self.orientation = WatchOSOrientationStrategy()
    }
    
    @State private var showPredictionsSheet = false
    @State private var showPredictionsSheetLandscape = false
    @State private var sheetSize: PresentationDetent = .fraction(MIN_SHEET_FRACTION)

    @State private var error: Error?
    @State private var showErrorAlert = false
    @State private var errorMessage = ""

    @State private var hasPredicted = false
    @State private var isInDancesView: Bool = false
    @State private var isServerReachable = false
    
    var body: some View {
        NavigationStack {
            Spacer()
            Button(action: {
                if isServerReachable {
                    Task {
                        await recordAndClassify()
                    }
                } else {
                    showError("Unable to connect to server. Please try again later.")
                }
            }) {
                RecordButtonView(audioController: audioController,  strategy: self.strategy)
            }
            .buttonStyle(PlainButtonStyle())
            .disabled(audioController.isRecording || audioController.isClassifying)
            .sheet(isPresented: .constant(showPredictionsSheet && !isInDancesView)) {
                PredictionSheetView(viewModel: viewModel, selectedDetent: $sheetSize, orientationObserver: self.orientation, showPredictionSheetLandscape: $showPredictionsSheetLandscape)
            }
        }
        .task {
            do {
                try await viewModel.updateDances()
                isServerReachable = true
            } catch {
                isServerReachable = false
                
                showError("Unable to update dances! Please try again later.")
            }
        }
    }
    
    private func recordAndClassify() async {
        do {
            let predictions = try await audioController.recordAndClassify(duration: 3.0)

            await MainActor.run {
                viewModel.predictions = predictions
                sheetSize = .fraction(MAX_SHEET_FRACTION)
                showPredictionsSheet = true
                hasPredicted = true
            }
        } catch {
            print("Failed to record and classify audio: \(error.localizedDescription)")

            await MainActor.run {
                showError(error.localizedDescription)

                showPredictionsSheet = false
                hasPredicted = false
            }
        }
    }
    
    private func showError(_ message: String) {
        errorMessage = message
        showErrorAlert = true
    }
}

#Preview {
    let model: Model = Model()
    let viewModel: ViewModel = ViewModel(model: model)
    
    ContentView(viewModel: viewModel)
}
