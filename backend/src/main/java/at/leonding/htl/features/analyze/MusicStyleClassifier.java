package at.leonding.htl.features.analyze;

import jakarta.enterprise.context.ApplicationScoped;
import weka.classifiers.Classifier;
import weka.classifiers.trees.J48;
import weka.core.DenseInstance;
import weka.core.Instances;
import weka.core.Attribute;

import jakarta.inject.Inject;
import java.util.ArrayList;
import java.util.List;

@ApplicationScoped
public class MusicStyleClassifier {

    private Classifier classifier;
    private Instances dataset;
    private ArrayList<String> genreList;  // List of dynamic genres

    @Inject
    MusicFeatureService musicFeatureService;

    // Initialize Weka Instances with dynamic genre handling
    public void initDataset() {
        ArrayList<Attribute> attributes = new ArrayList<>();
        for (int i = 0; i < 30; i++) {  // Assuming 30 features (bins)
            attributes.add(new Attribute("feature" + i));
        }

        // Initialize the dynamic list of genres (class values)
        genreList = new ArrayList<>();
        Attribute classAttribute = new Attribute("class", genreList);
        attributes.add(classAttribute);

        dataset = new Instances("MusicStyles", attributes, 0);
        dataset.setClassIndex(dataset.numAttributes() - 1);
    }

    // Method to add a new genre if it doesn't exist
    private void addGenreIfNew(String genre) {
        if (!genreList.contains(genre)) {
            genreList.add(genre);  // Add new genre to the list
            dataset.insertAttributeAt(new Attribute("class", genreList), dataset.classIndex());  // Update the dataset
        }
    }

    // Add a feature vector and its corresponding genres to the dataset
    public void addInstance(List<Double> features, List<String> genres) {
        // Concatenate genres into a single string
        String concatenatedGenres = String.join(",", genres);

        // Dynamically add the concatenated genre if it's new
        addGenreIfNew(concatenatedGenres);

        DenseInstance instance = new DenseInstance(features.size() + 1);
        for (int i = 0; i < features.size(); i++) {
            instance.setValue(i, features.get(i));
        }
        instance.setValue(dataset.classAttribute(), concatenatedGenres);  // Set concatenated genres as the class value
        dataset.add(instance);
    }

    // Load data from the database and train the classifier
    public void trainModelFromDatabase() throws Exception {
        initDataset();
        List<MusicFeature> musicFeatures = musicFeatureService.getAllFeatureVectors();
        for (MusicFeature musicFeature : musicFeatures) {
            addInstance(musicFeature.getFeatureVector(), musicFeature.getGenres());
        }
        classifier = new J48();  // You can switch to other classifiers like RandomForest, SVM, etc.
        classifier.buildClassifier(dataset);
    }

    // Classify a new feature vector (predict its genres)
    public String classifyNewInstance(List<Double> features) throws Exception {
        DenseInstance instance = new DenseInstance(features.size() + 1);
        for (int i = 0; i < features.size(); i++) {
            instance.setValue(i, features.get(i));
        }
        instance.setDataset(dataset);
        double classIndex = classifier.classifyInstance(instance);
        return dataset.classAttribute().value((int) classIndex);  // Returns the predicted class (genres)
    }
}