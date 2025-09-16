import SwiftUI

protocol RecordButtonStrategy {
    var buttonRadius: CGFloat { get }
    var padding: CGFloat { get }
    func feedbackForRecording(_ isRecording: Bool) -> SensoryFeedback?
    func feedbackForClassifying(_ isClassifying: Bool) -> SensoryFeedback?
}
