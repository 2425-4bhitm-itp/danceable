import SwiftUI

struct PredictionsView: View {
    let queue = DispatchQueue(label: "at.danceable")
    
    @ObservedObject var viewModel: ViewModel
    
    var body: some View {
        List(viewModel.predictions) { prediction in
            PredictionView(prediction: prediction, viewModel: viewModel)
        }.task {
            let predictions: [Prediction] = [
                Prediction(id: 1, danceId: 1, confidence: 0.85, speedCategory: SpeedCategory.slow),
                Prediction(id: 3, danceId: 3, confidence: 0.32, speedCategory: SpeedCategory.medium),
                Prediction(id: 4, danceId: 4, confidence: 0.12, speedCategory: SpeedCategory.fast)
            ]
            
            viewModel.predictions = predictions
        }
    }
}

#Preview {
    let model: Model = Model()
    let viewModel: ViewModel = ViewModel(model: model)
    
    return DancesView(viewModel: viewModel)
}
