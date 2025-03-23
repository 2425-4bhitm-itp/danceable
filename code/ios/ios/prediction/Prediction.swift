enum SpeedCategory: String, Decodable {
    case slow = "slow"
    case medium = "medium"
    case fast = "fast"
}

func getImageForSpeedCategory(speedCategory: SpeedCategory) -> String {
    var imageSystemName: String;
    
    switch speedCategory {
    case .slow:
        imageSystemName = "tortoise.circle.fill"
    case .medium:
        imageSystemName = "hare.circle.fill"
    case .fast:
        imageSystemName = "bird.circle.fill"
    }
    
    return imageSystemName
}

struct Prediction: Identifiable, Decodable {
    var id: Int
    
    var danceId: Int
    var confidence: Double
    var speedCategory: SpeedCategory
}
