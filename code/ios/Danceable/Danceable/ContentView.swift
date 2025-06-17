import SwiftUI
import AVFoundation

let MIN_SHEET_FRACTION: CGFloat = 0.175
let MAX_SHEET_FRACTION: CGFloat = 0.7

struct ContentView: View {
    var viewModel: ViewModel
    
    var strategy: RecordButtonStrategy
    
    var audioController: AudioController
    
    var haptics: HapticsStrategy
    
    init(viewModel: ViewModel) {
        self.viewModel = viewModel
        
        #if os(watchOS)
            self.haptics = WatchOSHapticsStrategy()
            self.audioController = AudioController(numberOfSoundLevels: 7)
            self.strategy = WatchRecordButtonStrategy()
        #else
            self.haptics = iOSHapticsStrategy()
            self.audioController = AudioController(hapticsStrategy: haptics)
            self.strategy = iOSRecordButtonStrategy()
        #endif
    }

    @StateObject private var orientationObserver = OrientationObserver()
    
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
        ZStack {
            Color("myBackground")
                .ignoresSafeArea()
            NavigationStack {
                Spacer()
                Button(action: {
                    if isServerReachable {
                        Task {
                            await recordAndClassify()
                            haptics.playDuolingoVibe()
                        }
                    } else {
                        showError("Unable to connect to server. Please try again later.")
                    }
                }) {
                    RecordButtonView(audioController: audioController, strategy: strategy, orientationObserver:  orientationObserver)
                }
                .disabled(audioController.isRecording || audioController.isClassifying)
                .sheet(isPresented: .constant(showPredictionsSheet && !isInDancesView && (orientationObserver.orientation.isPortrait || showPredictionsSheetLandscape))) {
                    PredictionSheetView(viewModel: viewModel, selectedDetent: $sheetSize, orientationObserver: orientationObserver, showPredictionSheetLandscape: $showPredictionsSheetLandscape)
                }
                Spacer()
                Spacer()
                Spacer()
                .toolbar {
                    ToolbarItem(placement: .topBarLeading) {
                        DancesNavigationLinkView(viewModel: viewModel, showPredictionsSheet: $showPredictionsSheet, hasPredicted: $hasPredicted, isInDancesView: $isInDancesView)
                    }
                }
            }
        }
        .alert("Error", isPresented: $showErrorAlert) {
            Button("OK", role: .cancel) { }
        } message: {
            Text(errorMessage)
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
        .onChange(of: orientationObserver.orientation, initial:false) { newOrientation,hasChanged  in
            print("Orientation changed to: \(newOrientation.rawValue)")
        }
    }

    private func recordAndClassify() async {
        do {
            let predictions = try await audioController.recordAndClassify(duration: 3.0)

            await MainActor.run {
                viewModel.predictions = predictions
                pullPredictionsSheet()
                hasPredicted = true
            }
        } catch {
            print("Failed to record and classify audio: \(error.localizedDescription)")

            await MainActor.run {
                showError(error.localizedDescription)

                closePredictionsSheet()
                hasPredicted = false
            }
        }
    }
    
    private func showError(_ message: String) {
        errorMessage = message
        showErrorAlert = true
    }
    
    private func pullPredictionsSheet() {
        sheetSize = .fraction(MAX_SHEET_FRACTION)
        showPredictionsSheet = true
        showPredictionsSheetLandscape = true
    }
    
    private func closePredictionsSheet() {
        showPredictionsSheet = false
        showPredictionsSheetLandscape = false
    }
}

#Preview {
    let model: Model = Model()
    let viewModel: ViewModel = ViewModel(model: model)
    
    return ContentView(viewModel: viewModel)
}
