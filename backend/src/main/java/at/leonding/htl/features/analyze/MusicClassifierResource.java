package at.leonding.htl.features.analyze;

import jakarta.inject.Inject;
import jakarta.ws.rs.POST;
import jakarta.ws.rs.Path;
import java.util.List;

@Path("/train")
public class MusicClassifierResource {

    @Inject
    MusicFeatureService musicFeatureService;

    MusicStyleClassifier classifier;  // Your existing classifier class

    @POST
    public String trainModel() throws Exception {
        List<MusicFeature> musicFeatures = musicFeatureService.getAllFeatureVectors();

        // Prepare dataset from database records
        classifier.initDataset();
        for (MusicFeature feature : musicFeatures) {
            classifier.addInstance(feature.featureVector, feature.genre);
        }

        // Train the classifier
        classifier.trainModel();
        return "Model trained successfully!";
    }
}
