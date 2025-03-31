import SwiftUI

struct DanceView: View {
    var dance: Dance
    var body: some View {
        VStack {
            Text(dance.name)
            HStack {
                Text("min bpm: \(String(describing: dance.minBpm))")
                Text("max bpm: \(String(describing: dance.maxBpm))")
            }.padding()
        }.padding()
    }
}

#Preview {
    DanceView(dance: Dance(id: 1, name: "cha cha cha", minBpm: 10, maxBpm: 100))
}
