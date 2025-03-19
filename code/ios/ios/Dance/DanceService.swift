import Foundation

let DANCES_BASE_URL = "http://localhost:8080/dances"

func loadDances() -> [Dance] {
    var dances: [Dance] = []
    
    if let url = URL(string: DANCES_BASE_URL) {
        if let data = try? Data(contentsOf: url) {
            let decoder = JSONDecoder();
            if let downloadedDances = try? decoder.decode([Dance].self, from: data) {
                dances = downloadedDances;
            } else {
                print("Something went wrong when parsing data from " + DANCES_BASE_URL)
            }
        } else {
            print("Something went wrong when trying to get data from " + DANCES_BASE_URL)
        }
    } else {
        print("Url " + DANCES_BASE_URL + " seems to be not valid!")
    }
    
    return dances;
}

func loadDanceSettings() -> [DanceSetting] {
    let dances: [Dance] = loadDances()
    
    return dances.map { d in DanceSetting(dance: d) }
}
