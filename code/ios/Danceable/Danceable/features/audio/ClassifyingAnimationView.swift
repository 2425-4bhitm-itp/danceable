import SwiftUI

struct ClassifyingAnimationView: View {
    var body: some View {
        ZStack {
            ProgressView()
                .progressViewStyle(CircularProgressViewStyle(tint: .white))
                .scaleEffect(2.0, anchor: .center)
        }
    }
}

#Preview {
    ClassifyingAnimationView()
}
