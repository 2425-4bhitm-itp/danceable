import Foundation
import AVFoundation
import SwiftUI
import Accelerate

class AudioRecorder: ObservableObject {
    private let engine = AVAudioEngine()
    private var audioFile: AVAudioFile?
    
    @Published var soundLevels: [CGFloat]
    
    init(numberOfSoundLevels: Int) {
        soundLevels = Array(repeating: 0.0, count: numberOfSoundLevels)
    }
    
    func startRecording(length: Double, outputURLString: String, completion: @escaping (Result<URL, Error>) -> Void) {
        let documentsDirectory = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
        let fileURL = documentsDirectory.appendingPathComponent(outputURLString)

        do {
            try FileManager.default.createDirectory(at: fileURL.deletingLastPathComponent(), withIntermediateDirectories: true)
        } catch {
            completion(.failure(error))
            return
        }

        if FileManager.default.fileExists(atPath: fileURL.path) {
            do {
                try FileManager.default.removeItem(at: fileURL)
            } catch {
                completion(.failure(error))
                return
            }
        }

        let inputNode = engine.inputNode
        let format = inputNode.outputFormat(forBus: 0)

        do {
            audioFile = try AVAudioFile(forWriting: fileURL, settings: format.settings)
        } catch {
            completion(.failure(error))
            return
        }

        inputNode.installTap(onBus: 0, bufferSize: 1024, format: format) { [weak self] buffer, _ in
            guard let self = self else { return }
            do {
                try self.audioFile?.write(from: buffer)
            } catch {
                print("Audio write error: \(error)")
            }
            self.processSoundLevel(from: buffer)
        }

        do {
            let session = AVAudioSession.sharedInstance()
            
            #if os(iOS)
            try session.setCategory(.playAndRecord, mode: .default, options: [.defaultToSpeaker])
            #else
            try session.setCategory(.playAndRecord, mode: .default)
            #endif
            
            try session.setActive(true)
            try engine.start()
        } catch {
            completion(.failure(error))
            return
        }

        DispatchQueue.main.asyncAfter(deadline: .now() + length) { [weak self] in
            guard let self = self else { return }
            self.stopRecording()
            completion(.success(fileURL))
        }
    }

    func stopRecording() {
        engine.inputNode.removeTap(onBus: 0)
        engine.stop()
    }
    
    func resetSoundLevels() {
        
    }

    private func processSoundLevel(from buffer: AVAudioPCMBuffer) {
        guard let channelData = buffer.floatChannelData?[0] else { return }

        var rms: Float = 0
        vDSP_rmsqv(channelData, 1, &rms, vDSP_Length(buffer.frameLength))

        let avgPower = 20 * log10(rms)
        let normalized = normalize(avgPower)
        let smoothed = generateSmoothedLevels(from: normalized)

        DispatchQueue.main.async {
            self.soundLevels = smoothed
        }
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
}
