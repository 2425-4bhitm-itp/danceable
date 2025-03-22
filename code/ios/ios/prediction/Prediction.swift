struct Prediction: Identifiable, Decodable {
    var id: Int
    
    var danceId: Int
    var confidence: Double
}
