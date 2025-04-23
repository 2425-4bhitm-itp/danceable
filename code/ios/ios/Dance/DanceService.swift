import Foundation

let DANCE_URL = Config.API_URL + "/dances"

func loadDances() -> [Dance] {
    var dances: [Dance] = []
    
    if let url = URL(string: DANCE_URL) {
        if let data = try? Data(contentsOf: url) {
            let decoder = JSONDecoder();
            if let downloadedDances = try? decoder.decode([Dance].self, from: data) {
                dances = downloadedDances;
            } else {
                print("Something went wrong when parsing data from " + DANCE_URL)
            }
        } else {
            print("Something went wrong when trying to get data from " + DANCE_URL)
        }
    } else {
        print("Url " + DANCE_URL + " seems to be not valid!")
    }
    
    return dances;
}
