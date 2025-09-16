import SwiftUI
    
struct SoundBarView: View {
    var soundLevel: CGFloat
    var width: CGFloat = 6.5
    
    var body: some View {
        let height = soundLevel * 250
        let opacity = height < width / 2 ? 0 : 1.0
        
        RoundedRectangle(cornerRadius: 100)
            .fill(Color.white)
            .frame(
                width: width,
                height: height
            )
            .opacity(opacity)
            .animation(.easeInOut(duration: 0.1), value: soundLevel)
            .animation(.easeInOut(duration: 0.1), value: opacity)
    }
}

#Preview {
    SoundBarView(soundLevel: 0.5)
}
