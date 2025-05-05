import Foundation
import AVFoundation
import Combine
import SwiftUI

class AudioRecorder: ObservableObject {
    var engine = AVAudioEngine()
    var audioFile: AVAudioFile?

    @Published var soundLevels: [CGFloat] = Array(repeating: 0.0, count: 11)

    func startRecording(length: Double, outputURLString: String, completion: @escaping (Result<URL, Error>) -> Void) {
        let input = engine.inputNode
        let format = input.outputFormat(forBus: 0)

        let documentsDirectory = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
        let outputFileURL = documentsDirectory.appendingPathComponent(outputURLString)

        let wavSettings: [String: Any] = [
            AVFormatIDKey: kAudioFormatLinearPCM,
            AVSampleRateKey: format.sampleRate,
            AVNumberOfChannelsKey: format.channelCount,
            AVLinearPCMBitDepthKey: 16,
            AVLinearPCMIsBigEndianKey: false,
            AVLinearPCMIsFloatKey: false,
            AVLinearPCMIsNonInterleaved: false
        ]

        DispatchQueue.global(qos: .userInitiated).async {
            do {
                self.audioFile = try AVAudioFile(forWriting: outputFileURL, settings: wavSettings)
            } catch {
                DispatchQueue.main.async {
                    completion(.failure(error))
                }
                return
            }

            input.installTap(onBus: 0, bufferSize: 1024, format: format) { buffer, _ in
                do {
                    try self.audioFile?.write(from: buffer)
                } catch {
                    print("Error writing buffer: \(error)")
                }

                guard let channelData = buffer.floatChannelData?[0] else { return }
                let frameLength = Int(buffer.frameLength)
                let samples = stride(from: 0, to: frameLength, by: buffer.stride).map {
                    channelData[$0]
                }

                let rms = sqrt(samples.map { $0 * $0 }.reduce(0, +) / Float(frameLength))
                let db = 20 * log10(rms)
                let normalized = self.normalize(db)

                let newLevels = self.generateSmoothedLevels(from: normalized)
                DispatchQueue.main.async {
                    self.soundLevels = newLevels
                }
            }

            do {
                try self.engine.start()
            } catch {
                DispatchQueue.main.async {
                    completion(.failure(error))
                }
                return
            }

            DispatchQueue.main.asyncAfter(deadline: .now() + length) {
                self.engine.stop()
                input.removeTap(onBus: 0)

                DispatchQueue.main.async {
                    completion(.success(outputFileURL))
                }
            }
        }
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

    private func normalize(_ db: Float) -> CGFloat {
        let clamped = max(0, CGFloat(db + 50) / 50)
        return min(clamped, 1.0)
    }
}
