import Foundation

class ViewModel: ObservableObject {
    @Published var model: Model
    
    var danceSettings: [DanceSetting] {
        get {
            model.danceSettings
        }
        set {
            model.danceSettings = newValue
        }
    }
    
    init(model: Model) {
        self.model = model
    }
}
