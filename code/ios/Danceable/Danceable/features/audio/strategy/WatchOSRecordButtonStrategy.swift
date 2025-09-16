import SwiftUI

struct WatchRecordButtonStrategy: RecordButtonStrategy {
    var buttonRadius: CGFloat { 175 }
    var padding: CGFloat { 0 }

    func feedbackForRecording(_ isRecording: Bool) -> SensoryFeedback? {
        isRecording ? .start : .stop
    }

    func feedbackForClassifying(_ isClassifying: Bool) -> SensoryFeedback? {
        isClassifying ? .impact(weight: .medium, intensity: 2.5) :
                        .impact(flexibility: .rigid, intensity: 20)
    }
}
