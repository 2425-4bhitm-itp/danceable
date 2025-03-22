import Foundation

let ADRESS = "localhost"
let PREDICTION_BASE_URL = "http://" + ADRESS + ":8080/predictions"

func loadPredictions() -> [Prediction] {
    var predictions: [Prediction] = []
    
    if let url = URL(string: PREDICTION_BASE_URL) {
        if let data = try? Data(contentsOf: url) {
            let decoder = JSONDecoder();
            if let downloadedPredictions = try? decoder.decode([Prediction].self, from: data) {
                predictions = downloadedPredictions;
            } else {
                print("Something went wrong when parsing data from " + PREDICTION_BASE_URL)
            }
        } else {
            print("Something went wrong when trying to get data from " + PREDICTION_BASE_URL)
        }
    } else {
        print("Url " + PREDICTION_BASE_URL + " seems to be not valid!")
    }
    
    return predictions;
}
