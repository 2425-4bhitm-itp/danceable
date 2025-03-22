import Foundation

var BASE_MAC_STATIC_IP_ADRESS = "localhost"
let DANCES_BASE_URL = "http://" + BASE_MAC_STATIC_IP_ADRESS + ":8080/dances"

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
