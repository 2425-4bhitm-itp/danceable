import SwiftUI

struct RecordButtonView: View {
    var isWatch: Bool = false
    @ObservedObject var audioController: AudioController
    @ObservedObject var orientationObserver = OrientationObserver()
    
    var isLandscape: Bool{
        //Raw Value 3 is normal portrait, need to compare like this because there is upside down Portrait which would not trigger.isLandscape
        return orientationObserver.orientation.rawValue != 3
    }
    
    var buttonRadius: CGFloat{
        // in order: watch size, landscape size, portrait size
        isWatch ? 175 : (isLandscape ? 225 : 200)
    }
    
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
                .fill(Color("mySecondary").opacity(0.5))
                .scaleEffect(animatePulse ? 1.2 : 1)
                .frame(
                    width: buttonRadius,
                    height: buttonRadius
                )

            Circle()
                .fill(Color("myPrimary"))
                .frame(
                    width: buttonRadius,
                    height: buttonRadius
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
            new ? (isWatch ? .start : .impact(weight: .light, intensity: 1 )) : .stop
        })
        .sensoryFeedback(trigger: audioController.isClassifying, { old, new in
            new ? .impact(weight: .medium, intensity: 2.5) : .impact(flexibility: .rigid, intensity: 20)
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
