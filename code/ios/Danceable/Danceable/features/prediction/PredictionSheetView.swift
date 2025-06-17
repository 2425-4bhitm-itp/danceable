import SwiftUI

struct PredictionSheetView: View {
    var viewModel: ViewModel
    @Binding var selectedDetent: PresentationDetent
    @ObservedObject var orientationObserver: OrientationObserver
    @Binding var showPredictionSheetLandscape : Bool
    
    
    
    var body: some View {
        VStack(spacing: 0) {
            if orientationObserver.orientation.isLandscape {
                HStack {
                    Button("Close") {
                        showPredictionSheetLandscape = false
                        selectedDetent = .fraction(MIN_SHEET_FRACTION)
                    }
                    .padding(.leading)
                    
                    Spacer()
                }
                .padding(.top, 10)
            }
            
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
    @Previewable @State var selectedDetent: PresentationDetent = .fraction(MIN_SHEET_FRACTION)

    @Previewable @State var showPredictionSheetLandscape: Bool = false
    @Previewable @State var orientationObserver: OrientationObserver = .init()
    
    let model = Model()
    let viewModel = ViewModel(model: model)
    
    PredictionSheetView(viewModel: viewModel, selectedDetent: $selectedDetent, orientationObserver: orientationObserver, showPredictionSheetLandscape: $showPredictionSheetLandscape)
}
