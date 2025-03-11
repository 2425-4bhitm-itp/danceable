import SwiftUI

struct ContentView: View {
    @ObservedObject var viewModel: ViewModel
    
    @State private var isSheetPresent: Bool = true
    @State private var selectedDetent: PresentationDetent = .fraction(0.1)
    
    var body: some View {
        Button(action: {
            selectedDetent = .fraction(0.6)
        }) {
            ZStack {
                Circle()
                    .fill(Color(red: 0.48, green: 0.14, blue: 0.58))
                Image(systemName: "microphone.fill")
                    .resizable()
                    .aspectRatio(contentMode: .fit)
                    .frame(width: 75)
                    .foregroundStyle(Color.white)
            }
            .padding(50)
            .shadow(radius: 10)
        }.sheet(isPresented: $isSheetPresent, content: {
            DancesView(viewModel: viewModel)
                .presentationDetents(
                    [.fraction(0.1), .fraction(0.6), .fraction(0.9)],
                    selection: $selectedDetent
                )
                .presentationBackgroundInteraction(
                    .enabled(upThrough: .fraction(0.1))
                )
                .presentationDragIndicator(.visible)
                .interactiveDismissDisabled(true)
        })
        .padding()
    }
}

#Preview {
    let model: Model = Model()
    let viewModel: ViewModel = ViewModel(model: model)
    
    return ContentView(viewModel: viewModel)
}
