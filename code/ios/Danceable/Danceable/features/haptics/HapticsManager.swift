import Foundation
import CoreHaptics

final class HapticsManager {
    static let shared = HapticsManager()
    private var engine: CHHapticEngine?
    
    private var loopingPlayer: CHHapticAdvancedPatternPlayer?

    private init() {
        prepareHapticsEngine()
    }
    
    private func prepareHapticsEngine() {
        guard CHHapticEngine.capabilitiesForHardware().supportsHaptics else { return }

        do {
            engine = try CHHapticEngine()
            engine?.playsHapticsOnly = true
            engine?.stoppedHandler = { reason in
                print("Haptic engine stopped: \(reason)")
            }
            engine?.resetHandler = { [weak self] in
                try? self?.engine?.start()
            }
            try engine?.start()
        } catch {
            print("Failed to prepare haptic engine:", error)
        }
    }
    
    func playPattern(_ pattern: CHHapticPattern) throws {
        guard CHHapticEngine.capabilitiesForHardware().supportsHaptics else { return }
        let player = try engine?.makePlayer(with: pattern)
        try player?.start(atTime: 0)
    }
    
    // MARK: Duolingo

    func playDuolingoVibe() {
        do {
            let pattern = try buildDuolingoPattern()
            try playPattern(pattern)
        } catch {
            print("Error playing Duolingo vibe:", error)
        }
    }

    private func buildDuolingoPattern() throws -> CHHapticPattern {
        let duration: TimeInterval = 1
        let steps = 7
        var events = [CHHapticEvent]()

        for i in 0..<steps {
            let t = Double(i) / Double(steps)
            let time = t * duration

            let sine = sin(t * .pi)
            let baseLevel = 0.6

            let intensity = baseLevel + (1.0 - baseLevel) * sine
            let sharpness = intensity

            let event = createPulse(
                intensity: Float(intensity),
                sharpness: Float(sharpness),
                relativeTime: time,
                duration: duration / Double(steps)
            )

            events.append(event)
        }

        return try CHHapticPattern(events: events, parameters: [])
    }


    private func createPulse(
        intensity: Float,
        sharpness: Float,
        relativeTime: TimeInterval,
        duration: TimeInterval
    ) -> CHHapticEvent {
        let parameters = [
            CHHapticEventParameter(parameterID: .hapticIntensity, value: intensity),
            CHHapticEventParameter(parameterID: .hapticSharpness, value: sharpness)
        ]

        return CHHapticEvent(
            eventType: .hapticContinuous,
            parameters: parameters,
            relativeTime: relativeTime,
            duration: duration
        )
    }
    
    // MARK: Agreesive Impact
    
    func playAggressiveImpact() {
        do {
            let pattern = try buildAggressivePattern()
            try playPattern(pattern)
        } catch {
            print("Error playing aggressive pattern:", error)
        }
    }
    
    private func buildAggressivePattern() throws -> CHHapticPattern {
        let events = [
            CHHapticEvent(
                eventType: .hapticTransient,
                parameters: [
                    CHHapticEventParameter(parameterID: .hapticIntensity, value: 1.0),
                    CHHapticEventParameter(parameterID: .hapticSharpness, value: 1.0)
                ],
                relativeTime: 0
            ),
            CHHapticEvent(
                eventType: .hapticTransient,
                parameters: [
                    CHHapticEventParameter(parameterID: .hapticIntensity, value: 0.8),
                    CHHapticEventParameter(parameterID: .hapticSharpness, value: 0.9)
                ],
                relativeTime: 0.1
            ),
            CHHapticEvent(
                eventType: .hapticTransient,
                parameters: [
                    CHHapticEventParameter(parameterID: .hapticIntensity, value: 0.6),
                    CHHapticEventParameter(parameterID: .hapticSharpness, value: 0.8)
                ],
                relativeTime: 0.2
            )
        ]
        return try CHHapticPattern(events: events, parameters: [])
    }
    
    // MARK: Smooth Wave

    func playSmoothWave() {
        do {
            let pattern = try buildSmoothWavePattern()
            try playPattern(pattern)
        } catch {
            print("Error playing smooth wave pattern:", error)
        }
    }

    private func buildSmoothWavePattern() throws -> CHHapticPattern {
        let duration: TimeInterval = 1.2
        let steps = 12
        var events = [CHHapticEvent]()

        for i in 0..<steps {
            let t = Double(i) / Double(steps)
            let time = t * duration

            let intensity: Double
            if t < 0.5 {
                intensity = t * 2 // linear ramp-up
            } else {
                intensity = (1.0 - t) * 2 // linear ramp-down
            }

            let sharpness = 0.3 + 0.5 * (1.0 - abs(t - 0.5) * 2)

            let event = createPulse(
                intensity: Float(intensity),
                sharpness: Float(sharpness),
                relativeTime: time,
                duration: duration / Double(steps)
            )
            events.append(event)
        }

        return try CHHapticPattern(events: events, parameters: [])
    }
    
    // MARK: Fade Out
    
    func playFadeOutPulse() {
        do {
            let pattern = try buildFadeOutPattern()
            try playPattern(pattern)
        } catch {
            print("Error playing fade-out pattern:", error)
        }
    }

    
    private func buildFadeOutPattern() throws -> CHHapticPattern {
        let duration: TimeInterval = 1.0
        let steps = 8
        var events = [CHHapticEvent]()

        for i in 0..<steps {
            let t = Double(i) / Double(steps)
            let time = t * duration

            let intensity = 1.0 - t // starts at 1.0, goes to 0.0
            let sharpness = 0.8 - t * 0.5 // fades from sharp to soft

            let event = createPulse(
                intensity: Float(intensity),
                sharpness: Float(sharpness),
                relativeTime: time,
                duration: duration / Double(steps)
            )
            events.append(event)
        }

        return try CHHapticPattern(events: events, parameters: [])
    }

    // MARK: Looping
    
    func startLoopingVibration() {
        guard CHHapticEngine.capabilitiesForHardware().supportsHaptics else { return }

        do {
            let pattern = try buildLoopingPattern()
            loopingPlayer = try engine?.makeAdvancedPlayer(with: pattern)
            try loopingPlayer?.start(atTime: 0)
        } catch {
            print("Error starting looping vibration:", error)
        }
    }

    func stopLoopingVibration() {
        do {
            try loopingPlayer?.stop(atTime: 0)
        } catch {
            print("Error stopping looping vibration:", error)
        }
        loopingPlayer = nil
    }

    private func buildLoopingPattern() throws -> CHHapticPattern {
        let event = CHHapticEvent(
            eventType: .hapticContinuous,
            parameters: [
                CHHapticEventParameter(parameterID: .hapticIntensity, value: 0.6),
                CHHapticEventParameter(parameterID: .hapticSharpness, value: 0.6)
            ],
            relativeTime: 0,
            duration: 3
        )
        return try CHHapticPattern(events: [event], parameters: [])
    }
}
