import SwiftUI

struct DancesNavigationLinkView: View {
    var viewModel: ViewModel
    @Binding var isSheetPresent: Bool
    @Binding var hasPredicted: Bool
    
    var body: some View {
        NavigationLink(destination: {
            Text("Available Dances").font(.headline)
            DancesView(viewModel: viewModel)
            .onAppear {
                isSheetPresent = false
            }.onDisappear {
                isSheetPresent = hasPredicted
            }
        }) {
            Image(systemName: "list.bullet.circle.fill")
                .resizable()
                .frame(width: 30, height: 30)
        }
    }
}

#Preview {
    @Previewable @State var isSheetPresent = false
    @Previewable @State var hasPredicted = false
    
    let model = Model()
    let viewModel = ViewModel(model: model)
    
    DancesNavigationLinkView(viewModel: viewModel, isSheetPresent: $isSheetPresent, hasPredicted: $hasPredicted)
}
