package at.leonding.htl.features.analyze;

import weka.classifiers.Classifier;
import weka.classifiers.trees.J48;
import weka.core.DenseInstance;
import weka.core.Instances;
import weka.core.Attribute;

import java.util.ArrayList;

public class MusicStyleClassifier {

    private Classifier classifier;
    private Instances dataset;
    private ArrayList<String> genreList;  // List of dynamic genres

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

    // Add a feature vector and its corresponding genre to the dataset
    public void addInstance(double[] features, String genre) {
        // Dynamically add the genre if it's new
        addGenreIfNew(genre);

        DenseInstance instance = new DenseInstance(features.length + 1);
        for (int i = 0; i < features.length; i++) {
            instance.setValue(i, features[i]);
        }
        instance.setValue(dataset.classAttribute(), genre);  // Set genre as the class value
        dataset.add(instance);
    }

    // Train a decision tree classifier (J48)
    public void trainModel() throws Exception {
        classifier = new J48();  // You can switch to other classifiers like RandomForest, SVM, etc.
        classifier.buildClassifier(dataset);
    }

    // Classify a new feature vector (predict its genre)
    public String classifyNewInstance(double[] features) throws Exception {
        DenseInstance instance = new DenseInstance(features.length + 1);
        for (int i = 0; i < features.length; i++) {
            instance.setValue(i, features[i]);
        }
        instance.setDataset(dataset);
        double classIndex = classifier.classifyInstance(instance);
        return dataset.classAttribute().value((int) classIndex);  // Returns the predicted class (genre)
    }
}
