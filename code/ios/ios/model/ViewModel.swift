import Foundation

class ViewModel: ObservableObject {
    @Published var model: Model

    var dances: [Dance] {
        get {
            model.dances
        }
        set {
            DispatchQueue.main.async {
                self.model.dances = newValue
            }
        }
    }

    var predictions: [Prediction] {
        get {
            model.prediction
        }
        set {
            DispatchQueue.main.async {
                self.model.prediction = newValue
            }
        }
    }

    init(model: Model) {
        self.model = model
    }
}
