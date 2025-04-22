import Foundation
import AVFoundation

class AudioRecorder: ObservableObject {
    var engine = AVAudioEngine()
    var audioFile: AVAudioFile?
    
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

        recordingQueue.async {
            do {
                self.audioFile = try AVAudioFile(forWriting: outputFileURL, settings: wavSettings)
            } catch {
                print("Error creating audio file: \(error)")
                DispatchQueue.main.async {
                    completion(.failure(error))
                }
                return
            }

            input.installTap(onBus: 0, bufferSize: 4096, format: format) { buffer, _ in
                do {
                    try self.audioFile?.write(from: buffer)
                } catch {
                    print("Error writing buffer: \(error)")
                }
            }

            do {
                try self.engine.start()
            } catch {
                print("Engine start failed: \(error)")
                DispatchQueue.main.async {
                    completion(.failure(error))
                }
                return
            }

            DispatchQueue.main.asyncAfter(deadline: .now() + length) {
                self.engine.stop()
                self.engine.reset()
                input.removeTap(onBus: 0)
                
                print("Recording finished. File saved at: \(outputFileURL)")
                completion(.success(outputFileURL))
            }
        }
    }
}
