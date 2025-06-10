import SwiftUI

struct PredictionSheetView: View {
    var viewModel: ViewModel
    @Binding var selectedDetent: PresentationDetent
    
    var body: some View {
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

#Preview {
    @Previewable @State var selectedDetent: PresentationDetent = .fraction(MIN_SHEET_FRACTION)
    
    let model = Model()
    let viewModel = ViewModel(model: model)
    
    PredictionSheetView(viewModel: viewModel, selectedDetent: $selectedDetent)
}
