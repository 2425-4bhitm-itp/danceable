package at.leonding.htl.features.analyze;

import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;
import java.util.List;

@ApplicationScoped
public class MusicFeatureService {

    @Inject
    MusicFeatureRepository repository;

    // Save feature vector and genre in database
    public void saveFeatureVector(double[] featureVector, String genre) {
        MusicFeature musicFeature = new MusicFeature();
        musicFeature.genre = genre;
        musicFeature.featureVector = featureVector;  // Ensure this line is correctly setting the feature vector
        repository.persist(musicFeature);
    }

    // Retrieve all feature vectors and genres for training
    public List<MusicFeature> getAllFeatureVectors() {
        return repository.listAll();
    }
}