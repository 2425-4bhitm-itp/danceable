import Foundation
import Combine


class AudioController: ObservableObject {
    @Published var soundLevels: [CGFloat] = Array(repeating: 0.0, count: 10)
    @Published var isRecording = false

    private let recorder = AudioRecorder()
    private let uploader = AudioUploader()
    private var cancellables = Set<AnyCancellable>()

    init() {
        recorder.$soundLevels
            .receive(on: DispatchQueue.main)
            .assign(to: &$soundLevels)
    }

    func recordAndUploadAudio(duration: Double, fileName: String = UUID().uuidString + ".wav", completion: @escaping (Result<[Prediction], Error>) -> Void) {
        isRecording = true
        recorder.startRecording(length: duration, outputURLString: fileName) { result in
            switch result {
            case .success(let fileURL):
                print("Recording saved at: \(fileURL)")
                self.uploadFile(fileURL: fileURL, completion: completion)
            case .failure(let error):
                print("Recording failed: \(error.localizedDescription)")
                completion(.failure(error))
            }
            self.isRecording = false
        }
    }

    private func uploadFile(fileURL: URL, completion: @escaping (Result<[Prediction], Error>) -> Void) {
        uploader.upload(fileURL: fileURL)
    }
    
    
}
