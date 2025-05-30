import Foundation
import Combine

class AudioController: ObservableObject {
    private let recorder: AudioRecorder
    private let uploader = AudioUploader()
    
    @Published var soundLevels: [CGFloat] = []
    @Published var isRecording = false
 
    init() {
        var numberOfSoundLevels = 11
        
        #if os(watchOS)
            numberOfSoundLevels = 7
        #endif
        
        recorder = AudioRecorder(numberOfSoundLevels: numberOfSoundLevels)
        
        recorder.$soundLevels
            .receive(on: DispatchQueue.main)
            .assign(to: &$soundLevels)
    }

    func recordAndUploadAudio(duration: Double, fileName: String = UUID().uuidString + ".caf", completion: @escaping (Result<[Prediction], Error>) -> Void) {
        isRecording = true
        
        recorder.startRecording(length: duration, outputURLString: fileName) { result in
            switch result {
            case .success(let fileURL):
                print("Recording saved at: \(fileURL)")
                self.uploader.upload(fileURL: fileURL, completion: completion)
            case .failure(let error):
                print("Recording failed: \(error.localizedDescription)")
                completion(.failure(error))
            }
            
            self.isRecording = false
            self.recorder.soundLevels = Array(repeating: 0.0, count: self.recorder.soundLevels.count)
        }
    }
}
