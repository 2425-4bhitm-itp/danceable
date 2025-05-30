import Foundation
import CoreML

let decoder = JSONDecoder()

func predictUsingLocalModel(featuresArray: [Double]) -> [Prediction] {
    let aiModel = try? danceAi(configuration: MLModelConfiguration())
    
    //replace this with a get all dances route
    let danceIDs: [String: Int] = [
        "discofox": 1,
        "slowwaltz": 2,
        "viennawaltz": 3,
        "chacha": 4,
        "foxtrott": 5,
        "quickstep": 6,
        "salsa": 7,
        "rumba": 8,
        "samba": 9,
        "jive": 10
    ]
    
    print(featuresArray)
    
    let multiArray = (try? convertToMultiArray(featuresArray))!
    let apiPredictions = try? aiModel?.prediction(input: multiArray).classProbability
        
    let predictions = apiPredictions?.compactMap { (danceName, confidence) -> Prediction? in
        guard let danceId = danceIDs[danceName.lowercased()] else {
            return nil  // Skip if the dance name doesn't exist in the dictionary
        }
        
        return Prediction(
            danceId: danceId,
            confidence: confidence / 100,
            speedCategory: .slow // CHANGE THIS
        )
    }
    
    return predictions ?? []
}

func convertToMultiArray(_ array: [Double]) throws -> MLMultiArray {
    
    let shape = [NSNumber(value: array.count)] // Shape: [n]
    
    // Create the multi-array
    guard let multiArray = try? MLMultiArray(shape: shape, dataType: .double) else {
        throw NSError(domain: "com.yourapp", code: 1, userInfo: [NSLocalizedDescriptionKey: "Failed to create MLMultiArray"])
    }
    
    // Fill the multi-array with your double values
    for (index, value) in array.enumerated() {
        multiArray[index] = NSNumber(value: value)
    }
    
    return multiArray
}
