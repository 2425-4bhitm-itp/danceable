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
    
    // print(apiPredictions)
    
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

/*func predict(data: Data, onDevice: Bool) {
    let aiModel = try? danceAi(configuration: MLModelConfiguration())
    
    //replace this with a get all dances route
    let danceIDs: [String: Int] = [
        "Slow Waltz": 1,
        "Viennese Waltz": 2,
        "Foxtrott": 3,
        "Quickstep": 4,
        "Tango": 5,
        "Cha Cha Cha": 6,
        "Rumba": 7,
        "Samba": 8,
        "Jive": 9,
        "Blues Dance": 10,
        "Tango Argentino": 11,
        "Salsa": 12,
        "Bachata": 13
    ]
    
    if (onDevice) {
        let featureArray = (try? decoder.decode([Double].self, from:data)) ?? [0.0] // Default Value gets written every time
        
        print(featureArray)
        
        let multiArray = (try? convertToMultiArray(featureArray))!
        let predictions = try? aiModel?.prediction(input: multiArray).classProbability
        
        let allPredictions = predictions?.compactMap { (danceName, confidence) -> Prediction? in
            let danceId = danceIDs[danceName.lowercased()]
            
            return Prediction(
                danceId: danceId!,
                confidence: confidence,
                speedCategory: .slow // CHANGE THIS
            )
        }
        
        //let sortedPredictions = allPredictions!.sorted{$0.confidence > $1.confidence}
        // no need to sort here => gets sorted in view
        
        
        
        //Write this into Model!
        
    } else {
        do {
            let predictions = try decoder.decode([Prediction].self, from: data)
        } catch {
            let decodingError = NSError(domain: "Uploader", code: 1003, userInfo: [NSLocalizedDescriptionKey: "Failed to decode predictions"])
            print(decodingError)
        }
    }
    
}*/

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
