import SwiftUI

struct RecordButtonView: View {
    @ObservedObject var audioController: AudioController
    @State private var animatePulse = false

    var body: some View {
        ZStack {
            Circle()
                .fill(Color.purple.opacity(0.25))
                .scaleEffect(animatePulse ? 1.2 : 1)

            Circle()
                .fill(Color(red: 0.48, green: 0.14, blue: 0.58))

            if !audioController.isRecording {
                Image(systemName: "microphone.fill")
                    .resizable()
                    .aspectRatio(contentMode: .fit)
                    .frame(width: 60)
                    .foregroundStyle(Color.white)
            } else {
                RecordingAnimationView(soundLevels: audioController.soundLevels)
            }
        }
        .padding(75)
        .shadow(radius: 10)
        .onReceive(audioController.$isRecording) { isRecording in
            if isRecording {
                startPulsing()
            } else {
                stopPulsing()
            }
        }
    }

    private func startPulsing() {
        animatePulse = false
        DispatchQueue.main.async {
            withAnimation(.easeInOut(duration: 0.6).repeatForever(autoreverses: true)) {
                animatePulse = true
            }
        }
    }

    private func stopPulsing() {
        withAnimation(.easeInOut(duration: 0.3)) {
            animatePulse = false
        }
    }
}
