import SwiftUI

struct ContentView: View {
    @ObservedObject var viewModel: ViewModel
    
    @State private var isSheetPresent: Bool = true
    @State private var selectedDetent: PresentationDetent = .fraction(0.125)
    
    var body: some View {
        Spacer()
        Button(action: {
            selectedDetent = .fraction(1)
        }) {
            ZStack {
                Circle()
                    .fill(Color(red: 0.48, green: 0.14, blue: 0.58))
                Image(systemName: "microphone.fill")
                    .resizable()
                    .aspectRatio(contentMode: .fit)
                    .frame(width: 60)
                    .foregroundStyle(Color.white)
            }
            .padding(75)
            .shadow(radius: 10)
        }.sheet(isPresented: $isSheetPresent, content: {
            DancesView(viewModel: viewModel)
                .presentationDetents(
                    [.fraction(0.125), .fraction(0.7), .fraction(1)],
                    selection: $selectedDetent
                )
                .presentationBackgroundInteraction(
                    .enabled(upThrough: .fraction(0.125))
                )
                .presentationDragIndicator(.visible)
                .interactiveDismissDisabled(true)
        })
        .padding()
        Spacer()
        Spacer()
        Spacer()
    }
}

#Preview {
    let model: Model = Model()
    let viewModel: ViewModel = ViewModel(model: model)
    
    return ContentView(viewModel: viewModel)
}
