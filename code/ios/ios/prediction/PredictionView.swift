import SwiftUI

struct PredictionView: View {
    var prediction: Prediction
    
    @ObservedObject var viewModel: ViewModel
    
    var body: some View {
        if let dance = viewModel.dances.first(where: { $0.id == prediction.danceId }) {
            
            Text(dance.name).font(.title2)
        }
    }
}

#Preview {
    let model: Model = Model()
    let viewModel: ViewModel = ViewModel(model: model)
    
    PredictionView(prediction: Prediction(id: 1, danceId: 1, confidence: 0.5), viewModel: viewModel)
}
