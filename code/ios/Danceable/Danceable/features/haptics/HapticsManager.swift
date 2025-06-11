import Foundation
import CoreHaptics

final class HapticsManager: ObservableObject {
    private var engine: CHHapticEngine?

    init() {
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
                print("Haptic engine reset; restarting.")
                try? self?.engine?.start()
            }

            try engine?.start()
        } catch {
            print("Failed to prepare haptic engine:", error)
        }
    }

    func playDuolingoVibe() {
        do {
            let pattern = try buildDuolingoPattern()
            try playPattern(pattern)
        } catch {
            print("Error playing Duolingo vibe:", error)
        }
    }

    func playPattern(_ pattern: CHHapticPattern) throws {
        guard CHHapticEngine.capabilitiesForHardware().supportsHaptics else { return }

        let player = try engine?.makePlayer(with: pattern)
        try player?.start(atTime: 0)
    }

    private func buildDuolingoPattern() throws -> CHHapticPattern {
        let duration: TimeInterval = 1.5
        let steps = 10
        var events = [CHHapticEvent]()

        for i in 0..<steps {
            let time = Double(i) / Double(steps) * duration
            let intensity = sin(Double(i) / Double(steps) * .pi) // Smooth pulse wave
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
}
