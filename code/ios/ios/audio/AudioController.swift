import Foundation

class AudioController: ObservableObject {
    private let recorder = AudioRecorder()
    private let uploader = AudioUploader()

    func recordAndUploadAudio(duration: Double, fileName: String = UUID().uuidString + ".wav", completion: @escaping (Result<[Prediction], Error>) -> Void) {
        recorder.startRecording(length: duration, outputURLString: fileName) { result in
            switch result {
            case .success(let fileURL):
                print("Recording saved at: \(fileURL)")
                self.uploadFile(fileURL: fileURL, completion: completion)
            case .failure(let error):
                print("Recording failed: \(error.localizedDescription)")
                completion(.failure(error))
            }
        }
    }

    private func uploadFile(fileURL: URL, completion: @escaping (Result<[Prediction], Error>) -> Void) {
        uploader.upload(fileURL: fileURL) { result in
            switch result {
            case .success(let serverResponse):
                completion(.success(serverResponse))
            case .failure(let error):
                print("Upload failed: \(error.localizedDescription)")
                completion(.failure(error))
            }
        }
    }
}
