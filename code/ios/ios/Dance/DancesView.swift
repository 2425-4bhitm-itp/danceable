import SwiftUI

struct DancesView: View {    
    @ObservedObject var viewModel: ViewModel
    
    var body: some View {
        NavigationStack {
            List(viewModel.dances) { dance in
                NavigationLink(dance.name, value: dance)
            }
            .navigationDestination(for: Dance.self) { dance in
                DanceView(dance: dance)
            }
        }
    }
}

#Preview {
    let model: Model = Model()
    let viewModel: ViewModel = ViewModel(model: model)
    
    let dancesView = DancesView(viewModel: viewModel)
    return dancesView
}
