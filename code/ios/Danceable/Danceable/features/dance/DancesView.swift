import SwiftUI

struct DancesView: View {
    let queue = DispatchQueue(label: "at.leonding.htl.features.dances")
    
    var viewModel: ViewModel
    
    var body: some View {
        List(viewModel.dances, id: \.id) { dance in
            Text(dance.name)
        }
    }
}

#Preview {
    let model: Model = Model()
    let viewModel: ViewModel = ViewModel(model: model)
    
    let dancesView = DancesView(viewModel: viewModel)
    return dancesView
}
