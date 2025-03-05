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

struct Model {
    var dances: [Dance] = []
}
