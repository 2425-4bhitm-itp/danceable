import Foundation
import Combine

class AudioController: ObservableObject, AudioControllerProtocol {
    private let recorder: AudioRecorder
    private let uploader = AudioUploader()
    
    private let haptics: HapticsStrategy
    
    @Published var soundLevels: [CGFloat] = []
    @Published var isRecording = false
    @Published var isClassifying = false
 
    init(numberOfSoundLevels: Int = 11, hapticsStrategy: HapticsStrategy) {
        recorder = AudioRecorder(numberOfSoundLevels: numberOfSoundLevels)
        
        haptics = hapticsStrategy
        
        recorder.$soundLevels
            .receive(on: DispatchQueue.main)
            .assign(to: &$soundLevels)
        
    }
    
    func recordAndClassify(
        duration: Double,
        fileName: String = UUID().uuidString + ".caf"
    ) async throws -> [Prediction] {
        let predictions: [Prediction]

        let fileURL: URL
        
        do {
            defer {
                Task { @MainActor in
                    isRecording = false
                    recorder.soundLevels = Array(repeating: 0.0, count: recorder.soundLevels.count)
                }
            }
            
            await MainActor.run {
                isRecording = true
            }
            
            fileURL = try await recorder.record(length: duration, outputLocation: fileName)
            print("Recording saved at: \(fileURL)")
        } catch {
            print("Recording failed: \(error.localizedDescription)")
            throw error
        }
        
        
        
        do {
            defer {
                Task { @MainActor in
                    isClassifying = false
                    haptics.stopLoopingVibration()
                }
            }
            
            await MainActor.run {
                isClassifying = true
                haptics.startLoopingVibration()
            }
            
            if Config.ON_DEVICE {
                predictions = try await uploader.classifyOnDevice(fileURL: fileURL)
            } else {
                predictions = try await uploader.classify(fileURL: fileURL)
            }
        } catch {
            print("Classifaction failed: \(error.localizedDescription)")
            throw error
        }

        return predictions
    }

}
