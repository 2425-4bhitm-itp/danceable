import SwiftUI

struct RecordButtonView: View {
    var isWatch: Bool = false
    @ObservedObject var audioController: AudioController
    
    init(audioController: AudioController) {
        #if os(watchOS)
            isWatch = true
        #endif
        self.audioController = audioController
    }
    
    @State private var animatePulse = false

    var body: some View {
        ZStack {
            Circle()
                .fill(Color("secondary").opacity(0.5))
                .scaleEffect(animatePulse ? 1.2 : 1)
                .frame(
                    width: isWatch ? 175 : nil,
                    height: isWatch ? 175 : nil
                )

            Circle()
                .fill(Color("primary"))
                .frame(
                    width: isWatch ? 175 : nil,
                    height: isWatch ? 175 : nil
                )

            if audioController.isRecording {
                RecordingAnimationView(soundLevels: audioController.soundLevels)
            } else if audioController.isClassifying {
                ClassifyingAnimationView()
            } else {
                Image(systemName: "microphone.fill")
                    .resizable()
                    .aspectRatio(contentMode: .fit)
                    .frame(width: 60)
                    .foregroundStyle(Color.white)
            }
        }
        .padding(isWatch ? 0 : 75)
        .shadow(radius: 10)
        .onReceive(audioController.$isRecording) { isRecording in
            if isRecording {
                startPulsing()
            } else {
                stopPulsing()
            }
        }
        .sensoryFeedback(trigger: audioController.isRecording, { old, new in
            new ? (isWatch ? .start : .impact(weight: .light, intensity: 0.5)) : .stop
        })
        .sensoryFeedback(trigger: audioController.isClassifying, { old, new in
            new ? .impact(weight: .medium, intensity: 0.75) : .impact(flexibility: .rigid, intensity: 10)
        })
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
