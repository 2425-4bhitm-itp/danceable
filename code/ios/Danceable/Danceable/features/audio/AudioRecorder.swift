import Foundation
import AVFoundation
import SwiftUI
import Accelerate

class AudioRecorder: ObservableObject {
    private let engine = AVAudioEngine()
    private var audioFile: AVAudioFile?
    
    private var isRecording = false
    
    var numberOfSoundLevels: Int
    
    @Published var soundLevels: [CGFloat]
    
    init(numberOfSoundLevels: Int) {
        self.numberOfSoundLevels = numberOfSoundLevels
        soundLevels = AudioRecorder.emptySoundLevels(numberOfSoundLevels: numberOfSoundLevels)
    }
    
    func record(
        length: Double,
        outputLocation: String
    ) async throws -> URL {
        if isRecording {
            throw AVError(_nsError: NSError())
        }
        
        isRecording = true
        let documentsDirectory = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
        let fileURL = documentsDirectory.appendingPathComponent(outputLocation)
        
        try FileManager.default.createDirectory(
            at: fileURL.deletingLastPathComponent(),
            withIntermediateDirectories: true
        )
        
        if FileManager.default.fileExists(atPath: fileURL.path) {
            try FileManager.default.removeItem(at: fileURL)
        }
        
        let inputNode = engine.inputNode
            let format = inputNode.outputFormat(forBus: 0)

            audioFile = try AVAudioFile(forWriting: fileURL, settings: format.settings)

            inputNode.installTap(onBus: 0, bufferSize: 1024, format: format) { [weak self] buffer, _ in
                guard let self = self else { return }
                do {
                    try self.audioFile?.write(from: buffer)
                } catch {
                    print("Audio write error: \(error)")
                }
                
                self.soundLevels = self.processSoundLevel(from: buffer)
            }

            let session = AVAudioSession.sharedInstance()

            #if os(iOS)
            try session.setCategory(.playAndRecord, mode: .default, options: [.defaultToSpeaker])
            #else
            try session.setCategory(.playAndRecord, mode: .default)
            #endif

            try session.setActive(true)
            try engine.start()

            try await Task.sleep(nanoseconds: UInt64(length * 1_000_000_000))

            stopRecording()
            return fileURL
    }

    func stopRecording() {
        engine.inputNode.removeTap(onBus: 0)
        engine.stop()
        isRecording = false
    }

    private func processSoundLevel(from buffer: AVAudioPCMBuffer) -> [CGFloat] {
        guard let channelData = buffer.floatChannelData?[0] else { return AudioRecorder.emptySoundLevels(numberOfSoundLevels: numberOfSoundLevels) }

        var rms: Float = 0
        vDSP_rmsqv(channelData, 1, &rms, vDSP_Length(buffer.frameLength))

        let avgPower = 20 * log10(rms)
        let normalized = normalize(avgPower)
        let smoothed = generateSmoothedLevels(from: normalized)

        return smoothed
    }

    private func normalize(_ db: Float) -> CGFloat {
        let clamped = max(0, CGFloat(db + 50) / 50)
        return min(clamped, 1.0)
    }

    private func generateSmoothedLevels(from normalized: CGFloat) -> [CGFloat] {
        let count = self.soundLevels.count
        let center = count / 2

        return (0..<count).map { i in
            let distance = abs(i - center)
            let scale = 1.0 - (CGFloat(distance) / CGFloat(center)) * 0.75
            let jitter = CGFloat.random(in: -0.075...0.075)
            return min(max(normalized * scale + jitter, 0), 1)
        }
    }
    
    static func emptySoundLevels(numberOfSoundLevels: Int) -> [CGFloat] {
        return Array(repeating: 0.0, count: numberOfSoundLevels)
    }
}
