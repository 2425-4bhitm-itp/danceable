import SwiftUI

struct ClassifyingAnimationView: View {
    var body: some View {
        ZStack {
            ProgressView()
                .progressViewStyle(CircularProgressViewStyle(tint: .white))
                .controlSize(.large)
        }
    }
}

#Preview {
    ClassifyingAnimationView()
}
