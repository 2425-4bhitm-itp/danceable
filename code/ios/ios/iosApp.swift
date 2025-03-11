import SwiftUI

@main
struct iosApp: App {
    var model = Model()
    
    var body: some Scene {
        let viewModel: ViewModel = ViewModel(model: model)
        
        WindowGroup {
            ContentView(viewModel: viewModel)
        }
    }
}
