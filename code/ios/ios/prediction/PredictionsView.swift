import SwiftUI

struct PredictionsView: View {
    let queue = DispatchQueue(label: "at.danceable")
    
    @ObservedObject var viewModel: ViewModel
    
    var body: some View {
        List(viewModel.predictions.sorted { $0.confidence > $1.confidence }.prefix(3)) { prediction in
            PredictionView(prediction: prediction, viewModel: viewModel)
        }
    }
}

#Preview {
    let model: Model = Model()
    let viewModel: ViewModel = ViewModel(model: model)
    
    return DancesView(viewModel: viewModel)
}
