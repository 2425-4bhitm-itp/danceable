import SwiftUI

struct iOSRecordButtonStrategy: RecordButtonStrategy {
    var buttonRadius: CGFloat { 225 }
    var padding: CGFloat { 75 }

    func feedbackForRecording(_ isRecording: Bool) -> SensoryFeedback? {
        isRecording ? .impact(weight: .light, intensity: 1) : .stop
    }

    func feedbackForClassifying(_ isClassifying: Bool) -> SensoryFeedback? {
        isClassifying ? .impact(weight: .medium, intensity: 2.5) :
                        .impact(flexibility: .rigid, intensity: 20)
    }
}
