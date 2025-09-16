import SwiftUI

struct RecordingAnimationView: View {
    var soundLevels: [CGFloat] = Array(repeating: 0.0, count: 10)
    
    var body: some View {
        HStack {
            ForEach(soundLevels.indices, id: \.self) { index in
                SoundBarView(soundLevel: soundLevels[index])
                    .padding(1.25)
            }
        }
    }
}

#Preview {
    RecordingAnimationView()
}
