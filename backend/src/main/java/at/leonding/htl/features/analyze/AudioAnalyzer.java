package at.leonding.htl.features.analyze;

import org.jtransforms.fft.DoubleFFT_1D;
import javax.sound.sampled.*;
import java.io.File;
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

public class AudioAnalyzer {

    private static final int WINDOW_SIZE = 1024;  // Number of samples per window (adjustable)
    private static final double MIN_FREQUENCY = 20.0;   // Minimum frequency to analyze
    private static final double MAX_FREQUENCY = 2000.0; // Maximum frequency to analyze (adjust as needed)

    // Method to read an audio file and count frequency occurrences
    public void analyzeAudio(File audioFile) {
        try {
            // Open the audio file
            AudioInputStream audioInputStream = AudioSystem.getAudioInputStream(audioFile);
            AudioFormat format = audioInputStream.getFormat();
            int numChannels = format.getChannels();
            float sampleRate = format.getSampleRate();

            // Read the audio data into a byte array
            byte[] audioBytes = audioInputStream.readAllBytes();
            int numSamples = audioBytes.length / 2; // assuming 16-bit audio (2 bytes per sample)
            double[] audioData = new double[numSamples];

            // Convert byte array to PCM data (16-bit audio)
            for (int i = 0; i < numSamples; i++) {
                int low = audioBytes[2 * i];
                int high = audioBytes[2 * i + 1];
                int sample = (high << 8) | (low & 0xff);
                audioData[i] = sample / 32768.0; // normalize to range [-1, 1]
            }

            // HashMap to store frequency counts
            Map<Double, Integer> frequencyCounts = new HashMap<>();

            // Analyze the audio in windows
            int numWindows = numSamples / WINDOW_SIZE;
            DoubleFFT_1D fft = new DoubleFFT_1D(WINDOW_SIZE);

            for (int win = 0; win < numWindows; win++) {
                // Extract window data
                double[] windowData = new double[WINDOW_SIZE];
                System.arraycopy(audioData, win * WINDOW_SIZE, windowData, 0, WINDOW_SIZE);

                // Perform FFT on the window
                double[] fftData = new double[WINDOW_SIZE * 2]; // FFT requires 2x space
                System.arraycopy(windowData, 0, fftData, 0, WINDOW_SIZE);
                fft.realForward(fftData);

                // Analyze FFT result and count frequency occurrences
                for (int i = 0; i < WINDOW_SIZE / 2; i++) {
                    double real = fftData[2 * i];
                    double imag = fftData[2 * i + 1];
                    double magnitude = Math.sqrt(real * real + imag * imag);
                    double frequency = i * sampleRate / WINDOW_SIZE;

                    // Only consider frequencies within the target range
                    if (frequency >= MIN_FREQUENCY && frequency <= MAX_FREQUENCY && magnitude > 0.1) {
                        frequencyCounts.put(frequency, frequencyCounts.getOrDefault(frequency, 0) + 1);
                    }
                }
            }

            // Print frequency occurrence counts
            System.out.println("Frequency (Hz)\tCount");
            for (Map.Entry<Double, Integer> entry : frequencyCounts.entrySet()) {
                System.out.printf("%f\t%d%n", entry.getKey(), entry.getValue());
            }

        } catch (UnsupportedAudioFileException | IOException e) {
            e.printStackTrace();
        }
    }

    public static void main(String[] args) {
        AudioAnalyzer analyzer = new AudioAnalyzer();
        //File audioFile = new File("/home/it210190/Music/Utility-4x4-Kick.wav");
        //File audioFile = new File("/home/it210190/Music/HighHopes.wav");
        //File audioFile = new File("/home/it210190/Music/high_hopes.wav");
        //File audioFile = new File("/home/it210190/Music/Beautiful-Life.mp3");
        //File audioFile = new File("/home/it210190/Music/sixteenkick.wav");
        //File audioFile = new File("/home/it210190/Music/untitled1.wav");
        File audioFile = new File("/home/it210190/Music/untitled2.wav");
        analyzer.analyzeAudio(audioFile);
        System.out.println("Audio analysis completed.");
    }
}