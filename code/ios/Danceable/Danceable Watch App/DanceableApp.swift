import SwiftUI

@main
struct Danceable_Watch_AppApp: App {
    var model = Model()

    var body: some Scene {
        let viewModel: ViewModel = ViewModel(model: model)

        WindowGroup {
            ContentView(viewModel: viewModel)
        }
    }
}
