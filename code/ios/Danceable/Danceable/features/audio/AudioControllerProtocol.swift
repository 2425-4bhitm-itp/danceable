import Foundation
import Combine
import CoreGraphics

protocol AudioControllerProtocol: ObservableObject {
    var soundLevels: [CGFloat] { get set }
    var isRecording: Bool { get set }
    var isClassifying: Bool { get set }
    
    func recordAndClassify(duration: Double, fileName: String) async throws -> [Prediction]
}
