import Foundation

var BASE_URL = "localhost:8080"
let DANCE_URL = "http://" + BASE_URL + "/dances"

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
