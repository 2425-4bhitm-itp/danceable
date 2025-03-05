import Foundation

class ViewModel: ObservableObject {
    @Published var model: Model
    var dances: [Dance] {
        get {
            model.dances
        }
        set {
            model.dances = newValue
        }
    }
    
    init(model: Model) {
        self.model = model
    }
}
