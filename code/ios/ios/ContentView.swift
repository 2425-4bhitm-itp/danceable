import SwiftUI

struct ContentView: View {
    @ObservedObject var viewModel: ViewModel
    
    var body: some View {
        DancesView(viewModel: viewModel)
        HStack {
            Button("", systemImage: "clock.arrow.trianglehead.counterclockwise.rotate.90", action: {
                print("button pressed")
            })
            Spacer()
            Button("", systemImage: "gear", action: {
                print("button pressed")
            })
        }.padding([.leading, .trailing], 52)
        .padding([.top], 5)
    }
}

#Preview {
    let model: Model = Model()
    let viewModel: ViewModel = ViewModel(model: model)
    
    return ContentView(viewModel: viewModel)
}
