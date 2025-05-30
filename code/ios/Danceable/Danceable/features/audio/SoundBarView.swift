import SwiftUI
    
struct SoundBarView: View {
    var soundLevel: CGFloat
    var width: CGFloat = 6.5
    
    var body: some View {
        RoundedRectangle(cornerRadius: 100)
            .fill(Color.white)
            .frame(
                width: width,
                height: soundLevel * 250
            )
            .animation(.easeInOut(duration: 0.1), value: soundLevel)
    }
}

#Preview {
    SoundBarView(soundLevel: 0.5)
}
