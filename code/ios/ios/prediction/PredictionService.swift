import Foundation

let PREDICTION_URL = Config.API_URL + "/predictions"

func loadPredictions() -> [Prediction] {
    var predictions: [Prediction] = []
    
    
    if let url = URL(string: PREDICTION_URL) {
        if let data = try? Data(contentsOf: url) {
            let decoder = JSONDecoder();
            if let downloadedPredictions = try? decoder.decode([Prediction].self, from: data) {
                predictions = downloadedPredictions;
            } else {
                print("Something went wrong when parsing data from " + PREDICTION_URL)
            }
        } else {
            print("Something went wrong when trying to get data from " + PREDICTION_URL)
        }
    } else {
        print("Url " + PREDICTION_URL + " seems to be not valid!")
    }
    
    return predictions;
}
