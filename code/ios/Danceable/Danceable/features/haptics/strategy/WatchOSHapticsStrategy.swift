import Foundation
import WatchKit

final class WatchHapticsStrategy: HapticsStrategy {
    func playDuolingoVibe() {
        play(.success)
    }

    func playAggressiveImpact() {
        play(.failure)
    }

    func playSmoothWave() {
        play(.click)
    }

    func playFadeOutPulse() {
        play(.start)
    }

    func startLoopingVibration() {
        // no loop due to it not beeing supported
        play(.directionUp)
    }

    func stopLoopingVibration() {
        // not supported on watch os
        return
    }

    private func play(_ type: WKHapticType) {
        WKInterfaceDevice.current().play(type)
    }
}
