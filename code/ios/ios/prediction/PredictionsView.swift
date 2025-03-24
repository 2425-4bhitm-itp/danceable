import SwiftUI

struct PredictionsView: View {
    let queue = DispatchQueue(label: "at.danceable")
    
    @ObservedObject var viewModel: ViewModel
        
    var body: some View {
        List(viewModel.predictions) { prediction in
            PredictionView(prediction: prediction, viewModel: viewModel)
        }.task {
            queue.async(execute: {
                let predictions: [Prediction] = loadPredictions()
                
                DispatchQueue.main.async(execute: {
                    viewModel.predictions = predictions
                })
            })
        }
    }
}

#Preview {
    let model: Model = Model()
    let viewModel: ViewModel = ViewModel(model: model)
    
    return PredictionsView(viewModel: viewModel)
}
