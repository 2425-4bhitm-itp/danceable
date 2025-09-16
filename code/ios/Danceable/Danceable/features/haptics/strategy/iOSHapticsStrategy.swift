final class iOSHapticsStrategy: HapticsStrategy {
    private let manager = HapticsManager.shared

    func playDuolingoVibe() { manager.playDuolingoVibe() }
    func playAggressiveImpact() { manager.playAggressiveImpact() }
    func playSmoothWave() { manager.playSmoothWave() }
    func playFadeOutPulse() { manager.playFadeOutPulse() }
    func startLoopingVibration() { manager.startLoopingVibration() }
    func stopLoopingVibration() { manager.stopLoopingVibration() }
}
