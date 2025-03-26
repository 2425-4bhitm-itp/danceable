import SwiftUI

struct DancesView: View {
    let queue = DispatchQueue(label: "at.htl.leonding")
    
    @ObservedObject var viewModel: ViewModel
    
    var body: some View {
        NavigationStack {
            List(viewModel.dances) { dance in
                NavigationLink(dance.name, value: dance)
            }
            .navigationDestination(for: Dance.self) { dance in
                DanceView(dance: dance)
            }
        }.task {
            queue.async(execute: {
                let dances = loadDances()
                
                DispatchQueue.main.async(execute: {
                    viewModel.model.dances = dances
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
