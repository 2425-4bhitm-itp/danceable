package at.leonding.htl.features.analyze;

import jakarta.enterprise.context.ApplicationScoped;
import org.jtransforms.fft.DoubleFFT_1D;
import jakarta.inject.Inject;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.List;

@ApplicationScoped
public class AudioAnalyzer {

    @Inject
    VectorRepository vectorRepository; // Repository to access saved vectors

    // 1. Method to perform Fourier analysis and return the vector
    public double[] analyze(String filePath) throws IOException {
        // Read the WAV file and convert it into a double array for FFT
        byte[] audioBytes = Files.readAllBytes(Paths.get(filePath));
        double[] audioData = convertToDoubleArray(audioBytes);

        // Perform Fourier Transform
        DoubleFFT_1D fft = new DoubleFFT_1D(audioData.length);
        fft.realForward(audioData);

        return audioData; // Return the Fourier vector
    }

    // 2. Method to analyze a file and save the vector with the category in the database (learning phase)
    public void analyzeAndSave(String filePath, String category) throws IOException {
        double[] vector = analyze(filePath); // Perform analysis
        vectorRepository.saveVector(vector, category); // Save the vector and category
    }

    // 3. Method to analyze and categorize the file (classification phase)
    public String categorize(String filePath) throws IOException {
        double[] vector = analyze(filePath); // Get the vector for the new file

        // Retrieve all stored vectors from the database
        List<VectorEntity> allVectors = vectorRepository.listAll();

        // Compare the new vector with stored vectors to find the closest match
        VectorEntity closestMatch = findClosestMatch(vector, allVectors);

        // Return the category of the closest matching vector
        return closestMatch != null ? closestMatch.category : "Unknown category";
    }

    // Method to find the closest vector match from the database
    private VectorEntity findClosestMatch(double[] newVector, List<VectorEntity> storedVectors) {
        VectorEntity closestMatch = null;
        double minDistance = Double.MAX_VALUE;

        // Calculate the distance between vectors and find the closest one
        for (VectorEntity storedVector : storedVectors) {
            double distance = calculateDistance(newVector, storedVector.vector);
            if (distance < minDistance) {
                minDistance = distance;
                closestMatch = storedVector;
            }
        }
        return closestMatch;
    }

    // Method to calculate the Euclidean distance between two vectors
    private double calculateDistance(double[] vector1, double[] vector2) {
        double sum = 0.0;
        int length = Math.min(vector1.length, vector2.length); // Ensure matching lengths
        for (int i = 0; i < length; i++) {
            sum += Math.pow(vector1[i] - vector2[i], 2);
        }
        return Math.sqrt(sum);
    }

    // Convert audio bytes to double array (simplified for clarity)
    private double[] convertToDoubleArray(byte[] audioBytes) {
        double[] audioData = new double[100];
        for (int i = 0; i < 100; i++) {
            audioData[i] = (double) audioBytes[i];
        }
        return audioData;
    }
}
