package at.leonding.htl.features.analyze;

import jakarta.enterprise.context.ApplicationScoped;
import javax.sound.sampled.AudioInputStream;
import javax.sound.sampled.AudioSystem;
import org.jtransforms.fft.DoubleFFT_1D;
import java.io.IOException;
import java.io.InputStream;
import java.util.Arrays;
import java.util.List;
import java.util.logging.Level;
import java.util.logging.Logger;
import java.io.BufferedInputStream;
import java.util.stream.Collectors;
import java.util.stream.DoubleStream;

@ApplicationScoped
public class AudioFeatureExtractor {

    private static final int WINDOW_SIZE = 1024;  // Number of samples per window
    private static final int NUM_BINS = 30;       // Number of frequency bins to reduce features
    private static final Logger LOGGER = Logger.getLogger(AudioFeatureExtractor.class.getName());

    // Method to extract features from an uploaded audio InputStream
    public List<Double> extractFeatures(InputStream audioStream) {
        try (BufferedInputStream bufferedInputStream = new BufferedInputStream(audioStream)) {
            AudioInputStream audioInputStream = AudioSystem.getAudioInputStream(bufferedInputStream);
            int numSamples = (int) (audioInputStream.getFrameLength());
            double[] audioData = new double[numSamples];

            // Read audio data into a byte array and convert it to a normalized double array
            byte[] audioBytes = audioInputStream.readAllBytes();
            for (int i = 0; i < numSamples; i++) {
                int low = audioBytes[2 * i];
                int high = audioBytes[2 * i + 1];
                int sample = (high << 8) | (low & 0xff);
                audioData[i] = sample / 32768.0;  // Normalize to range [-1, 1]
            }

            // Initialize the feature vector
            double[] featureVector = new double[NUM_BINS];
            DoubleFFT_1D fft = new DoubleFFT_1D(WINDOW_SIZE);
            int numWindows = numSamples / WINDOW_SIZE;

            // Perform FFT for each window and aggregate results into frequency bins
            for (int win = 0; win < numWindows; win++) {
                double[] windowData = Arrays.copyOfRange(audioData, win * WINDOW_SIZE, (win + 1) * WINDOW_SIZE);
                double[] fftData = new double[WINDOW_SIZE * 2];
                System.arraycopy(windowData, 0, fftData, 0, WINDOW_SIZE);
                fft.realForward(fftData);

                // Aggregate FFT results into frequency bins
                for (int i = 0; i < WINDOW_SIZE / 2; i++) {
                    double real = fftData[2 * i];
                    double imag = fftData[2 * i + 1];
                    double magnitude = Math.sqrt(real * real + imag * imag);
                    int binIndex = (int) Math.floor((double) i / (WINDOW_SIZE / 2) * NUM_BINS);
                    featureVector[binIndex] += magnitude;
                }
            }

            // Normalize the feature vector
            for (int i = 0; i < NUM_BINS; i++) {
                featureVector[i] /= numWindows;
            }

            // Convert double[] to List<Double>
            return DoubleStream.of(featureVector).boxed().collect(Collectors.toList());

        } catch (IOException | javax.sound.sampled.UnsupportedAudioFileException e) {
            LOGGER.log(Level.SEVERE, "Error extracting features from audio stream", e);
        }

        return null;
    }
}