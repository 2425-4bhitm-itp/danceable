import SwiftUI

struct DancesView: View {
    let queue = DispatchQueue(label: "at.htl.leonding")
    
    @ObservedObject var viewModel: ViewModel
    
    var body: some View {
        NavigationStack {
            List(viewModel.danceSettings) { danceSetting in
                NavigationLink(danceSetting.dance.name, value: danceSetting.dance)
            }
            .navigationDestination(for: Dance.self) { dance in
                DanceView(dance: dance)
            }
        }.task {
            queue.async(execute: {
                let dances = loadDanceSettings()
                DispatchQueue.main.async(execute: {
                    viewModel.model.danceSettings = dances
                })
            })
        }
    }
}

#Preview {
    let model: Model = Model()
    let viewModel: ViewModel = ViewModel(model: model)
    
    let dancesView = DancesView(viewModel: viewModel)
    return dancesView
}
