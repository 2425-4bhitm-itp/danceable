package at.leonding.htl.features.analyze;

import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;
import java.util.Arrays;
import java.util.List;

@ApplicationScoped
public class MusicFeatureService {

    @Inject
    MusicFeatureRepository repository;

    // Save feature vector and genres in database
    public void saveFeatureVector(List<Double> featureVector, String genreString) {
        List<String> genres = Arrays.asList(genreString.split(","));
        MusicFeature musicFeature = new MusicFeature();
        musicFeature.setFeatureVector(featureVector);
        musicFeature.setGenres(genres);
        repository.persist(musicFeature);
    }

    // Retrieve all feature vectors and genres for training
    public List<MusicFeature> getAllFeatureVectors() {
        return repository.listAll();
    }
}