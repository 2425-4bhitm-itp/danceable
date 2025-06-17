import SwiftUI

struct RecordButtonView: View {
    @ObservedObject var audioController: AudioController
    @ObservedObject var orientationObserver: OrientationObserver
    
    private let strategy: RecordButtonStrategy
    @State private var animatePulse = false

    init(audioController: AudioController, strategy: RecordButtonStrategy, orientationObserver: OrientationObserver) {
        self.orientationObserver = orientationObserver
        self.audioController = audioController
        self.strategy = strategy
    }

    var body: some View {
        ZStack {
            Circle()
                .fill(Color("mySecondary").opacity(0.5))
                .scaleEffect(animatePulse ? 1.2 : 1)
                .frame(
                    width: strategy.buttonRadius,
                    height: strategy.buttonRadius
                )

            Circle()
                .fill(Color("myPrimary"))
                .frame(
                    width: strategy.buttonRadius,
                    height: strategy.buttonRadius
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
        .padding(strategy.padding)
        .shadow(radius: 10)
        .onReceive(audioController.$isRecording) { isRecording in
            isRecording ? startPulsing() : stopPulsing()
        }
        .sensoryFeedback(trigger: audioController.isRecording) { _, new in
            strategy.feedbackForRecording(new)
        }
        .sensoryFeedback(trigger: audioController.isClassifying) { _, new in
            strategy.feedbackForClassifying(new)
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
