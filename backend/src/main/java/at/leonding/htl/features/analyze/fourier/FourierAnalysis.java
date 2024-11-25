package at.leonding.htl.features.analyze.fourier;

import at.leonding.htl.features.dance.Dance;
import jakarta.inject.Singleton;

import javax.sound.sampled.*;
import java.io.BufferedInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.*;
import javax.sound.sampled.AudioInputStream;
import javax.sound.sampled.AudioSystem;
import javax.sound.sampled.UnsupportedAudioFileException;

@Singleton
public class FourierAnalysis {
    public static final double sampleRate = 44100.0;

    private final Map<Double, Double> frequencyMagnitudeMap = new HashMap<>();
    private Double bpm = 0.0;
    private static final List<String> danceTypes = new ArrayList<>();

    public void calculateValues(InputStream wavFile) throws UnsupportedAudioFileException, IOException {
        clearValues();

        double[] audioData = readWavFile(wavFile);

        Complex[] fftData = performFFT(audioData);

        double highestMagnitude = getHighestMagnitude(fftData);

        for (int i = 0; i < fftData.length / 2; i++) {
            double frequency = i * sampleRate / fftData.length;
            double magnitude = fftData[i].getAbs() / highestMagnitude;
            frequencyMagnitudeMap.put(frequency, magnitude);
        }

        Complex[] fftDataLimited = new Complex[fftData.length / 2000];
        System.arraycopy(fftData, 0, fftDataLimited, 0, fftDataLimited.length);

        bpm = calculateBPM(fftDataLimited, fftData.length);

        mapBpmToDance(bpm);
    }

    private void clearValues() {
        frequencyMagnitudeMap.clear();
        bpm = 0.0;
        danceTypes.clear();
    }

    public Map<Double, Double> getFrequencyMagnitudeMap() {
        return Collections.unmodifiableMap(frequencyMagnitudeMap);
    }

    public Double getBpm() {
        return bpm;
    }

    public List<String> getDanceTypes() {
        return Collections.unmodifiableList(danceTypes);
    }

    public static double[] readWavFile(InputStream inputStream) throws UnsupportedAudioFileException, IOException {
        BufferedInputStream bufferedInputStream = new BufferedInputStream(inputStream);
        AudioInputStream audioStream = AudioSystem.getAudioInputStream(bufferedInputStream);
        AudioFormat format = audioStream.getFormat();
        int bytesPerFrame = format.getFrameSize();
        long numFrames = audioStream.getFrameLength();
        double[] audioData = new double[(int) numFrames];

        byte[] buffer = new byte[bytesPerFrame];
        for (int i = 0; i < numFrames; i++) {
            audioStream.read(buffer, 0, bytesPerFrame);
            int sample = 0;
            for (int j = 0; j < buffer.length; j++) {
                sample += buffer[j] << (8 * j);
            }
            audioData[i] = sample / 32768.0; // 16-BIT
        }

        return audioData;
    }

    public static Complex[] performDFT(double[] audioData) {
        int N = 5000;
        Complex[] result = new Complex[N];

        for (int k = 0; k < N; k++) {
            double real = 0;
            double imaginary = 0;
            for (int t = 0; t < N; t++) {
                double angle = 2 * Math.PI * k * t / N;
                real += audioData[t] * Math.cos(angle);
                imaginary -= audioData[t] * Math.sin(angle);
            }
            result[k] = new Complex(real, imaginary);
        }
        return result;
    }

    public static double[] removeDCComponent(double[] audioData) {
        double sum = 0;
        for (double sample : audioData) {
            sum += sample;
        }
        double mean = sum / audioData.length;

        double[] adjustedAudioData = new double[audioData.length];
        for (int i = 0; i < audioData.length; i++) {
            adjustedAudioData[i] = audioData[i] - mean;
        }

        return adjustedAudioData;
    }

    public static Complex[] performFFT(double[] audioData) {
        double[] adjustedAudioData = removeDCComponent(audioData);

        int N = audioData.length;
        if (N == 0) return new Complex[0];

        // Find the next power of 2
        int powerOf2 = 1;
        while (powerOf2 < N) {
            powerOf2 *= 2;
        }

        // Pad the audioData array with zeros
        double[] paddedAudioData = new double[powerOf2];
        System.arraycopy(adjustedAudioData, 0, paddedAudioData, 0, N);

        Complex[] result = new Complex[powerOf2];
        for (int i = 0; i < powerOf2; i++) {
            result[i] = new Complex(paddedAudioData[i], 0);
        }

        fft(result);
        return result;
    }

    private static void fft(Complex[] x) {
        int N = x.length;

        if (N <= 1) return;

        if ((N & (N - 1)) != 0) throw new IllegalArgumentException("Length of x must be a power of 2");

        Complex[] even = new Complex[N / 2];
        Complex[] odd = new Complex[N / 2];
        for (int i = 0; i < N / 2; i++) {
            even[i] = x[2 * i];
            odd[i] = x[2 * i + 1];
        }

        fft(even);
        fft(odd);

        for (int k = 0; k < N / 2; k++) {
            double angle = -2 * Math.PI * k / N;
            Complex t = new Complex(Math.cos(angle), Math.sin(angle)).multiply(odd[k]);
            x[k] = even[k].add(t);
            x[k + N / 2] = even[k].subtract(t);
        }
    }

    private static int getPeakIndex(Complex[] fftData) {
        double highestMagnitude = 0;
        int peakIndex = 0;

        for (int i = 0; i < fftData.length; i++) {
            double magnitude = fftData[i].getAbs();
            if (magnitude > highestMagnitude) {
                highestMagnitude = magnitude;
                peakIndex = i;
            }
        }

        return peakIndex;
    }

    public static double calculateBPM(Complex[] fftData, int pointsToCalculate) {
        int lowerBoundIndex = (int) (0.65 * pointsToCalculate / sampleRate);
        int upperBoundIndex = (int) (2.5 * pointsToCalculate / sampleRate);

        double highestMagnitude = 0;
        int peakIndex = lowerBoundIndex;

        for (int i = lowerBoundIndex; i <= upperBoundIndex; i++) {
            double magnitude = fftData[i].getAbs();
            if (magnitude > highestMagnitude) {
                highestMagnitude = magnitude;
                peakIndex = i;
            }
        }

        double bpmFrequency = peakIndex * sampleRate / pointsToCalculate;

        return bpmFrequency * 60;
    }

    public static void mapBpmToDance(double bpm){
        ArrayList<Dance> dances = initDanceTypes();
        for(Dance dance : dances){
            if(dance.isBpmInRange(bpm)){
                danceTypes.add(dance.getName());
            }
        }
    }

    private static ArrayList<Dance> initDanceTypes(){
        ArrayList<Dance> dances = new ArrayList<>();

        Dance discofox = new Dance();
        discofox.setMinBpm(115);
        discofox.setMaxBpm(145);
        discofox.setName("Discofox");

        Dance foxtrott = new Dance();
        foxtrott.setMinBpm(80);
        foxtrott.setMaxBpm(115);
        foxtrott.setName("Foxtrott");

        Dance chacha = new Dance();
        chacha.setMinBpm(110);
        chacha.setMaxBpm(140);
        chacha.setName("Cha-Cha");

        Dance jive = new Dance();
        jive.setMinBpm(140);
        jive.setMaxBpm(180);
        jive.setName("Jive");

        Dance rumba = new Dance();
        rumba.setMinBpm(90);
        rumba.setMaxBpm(120);
        rumba.setName("Rumba");

        dances.add(discofox);
        dances.add(foxtrott);
        dances.add(chacha);
        dances.add(jive);
        dances.add(rumba);

        return dances;
    }

    public double getHighestMagnitude(Complex[] fftData) {
        int peakIndex = getPeakIndex(fftData);
        return fftData[peakIndex].getAbs();
    }
}