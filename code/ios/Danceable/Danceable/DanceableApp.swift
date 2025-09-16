import SwiftUI

@main
struct DanceableApp: App {
    var model = Model()
    
        var body: some Scene {
        let viewModel: ViewModel = ViewModel(model: model)

            WindowGroup {
            ContentView(viewModel: viewModel)
        }
    }
}
