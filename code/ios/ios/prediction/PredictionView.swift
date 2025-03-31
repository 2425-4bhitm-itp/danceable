import SwiftUI

struct PredictionView: View {
    var prediction: Prediction
    
    @ObservedObject var viewModel: ViewModel
    
    var body: some View {
        VStack {
            HStack {
                if let dance = viewModel.dances.first(where: { $0.id == prediction.danceId }) {
                    Text(dance.name).font(.title2)
                }
                Spacer()
                Image(systemName: getImageForSpeedCategory(for: prediction.speedCategory))
                    .resizable()
                    .frame(width: 24, height: 24)
            }
            
            HStack {
                ProgressView(value: prediction.confidence)
                Text(String(prediction.confidence * 100) + "%")
            }
        }
        .padding()
        .cornerRadius(8)
        .overlay(
            RoundedRectangle(cornerRadius: 8)
                .inset(by: 2)
                .stroke(.gray, lineWidth: 1)
        )
    }
}

#Preview {
    let model: Model = Model()
    let viewModel: ViewModel = ViewModel(model: model)
    
    PredictionView(prediction: Prediction(id: 1, danceId: 1, confidence: 0.75, speedCategory: SpeedCategory.slow), viewModel: viewModel)
}
