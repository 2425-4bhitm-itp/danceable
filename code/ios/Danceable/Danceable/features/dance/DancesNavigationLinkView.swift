import SwiftUI

struct DancesNavigationLinkView: View {
    var viewModel: ViewModel
    @Binding var showPredictionsSheet: Bool
    @Binding var hasPredicted: Bool
    @Binding var isInDancesView: Bool
    
    var body: some View {
        NavigationLink(destination: {
            Text("Available Dances").font(.headline)
            DancesView(viewModel: viewModel)
            .onAppear {
                isInDancesView = true
                showPredictionsSheet = false
            }
            .onDisappear {
                isInDancesView = false
                showPredictionsSheet = hasPredicted
            }
        }) {
            Image(systemName: "list.bullet.circle.fill")
                .resizable()
                .frame(width: 25, height: 25)
                .foregroundColor(Color("myAccent"))
        }
    }
}

#Preview {
    @Previewable @State var isSheetPresent = false
    @Previewable @State var hasPredicted = false
    @Previewable @State var isInDancesView = false

    let model = Model()
    let viewModel = ViewModel(model: model)
    
    DancesNavigationLinkView(viewModel: viewModel, showPredictionsSheet: $isSheetPresent, hasPredicted: $hasPredicted, isInDancesView: $isInDancesView)
}
