enum SpeedCategory: String, Decodable, CaseIterable {
    case slow = "slow"
    case medium = "medium"
    case fast = "fast"
}

let possibleSpeedImageSystemNames = [
    "tortoise.circle.fill",
    "hare.circle.fill",
    "bird.circle.fill"
]

struct Prediction: Identifiable, Decodable {
    var id:Int {danceId}
    var danceId: Int
    var confidence: Double
    var speedCategory: SpeedCategory
}

func getImageForSpeedCategory(for speedCategory: SpeedCategory) -> String {
    let index = SpeedCategory.allCases.firstIndex(of: speedCategory)!
    return possibleSpeedImageSystemNames[index]
}
