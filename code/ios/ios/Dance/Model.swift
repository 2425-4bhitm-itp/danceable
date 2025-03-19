struct Dance: Codable, Identifiable, Hashable {
    var id: Int
    var name: String
    var minBpm: Int
    var maxBpm: Int
    
    init(id: Int, name: String, minBpm: Int, maxBpm: Int) {
        self.id = id
        self.name = name
        self.maxBpm = maxBpm
        self.minBpm = minBpm
    }
}

struct DanceSetting: Identifiable {
    var id: Int
    var dance: Dance
    var isActive: Bool
    
    init(dance: Dance, isActive: Bool = true) {
        self.id = dance.id
        self.dance = dance
        self.isActive = isActive
    }
}

struct Model {
    var danceSettings: [DanceSetting] = []
}
