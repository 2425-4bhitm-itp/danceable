package at.leonding.htl.features.analyze.fourier;

import at.leonding.htl.features.dance.Dance;
import javafx.application.Application;
import javafx.scene.Scene;
import javafx.scene.chart.Axis;
import javafx.scene.chart.LineChart;
import javafx.scene.chart.NumberAxis;
import javafx.scene.chart.XYChart;
import javafx.stage.Stage;

import javax.sound.sampled.*;
import java.io.File;
import java.io.IOException;
import java.util.ArrayList;

public class FourierAnalysis extends Application {
    public static final double sampleRate = 44100.0;
    public static final int bpmPoints = 4000;

    public static void main(String[] args) {
        launch(args);
    }

    @Override
    public void start(Stage stage) throws Exception {
        //File wavFile = new File("/home/it210190/Music/exampleMusic/50hz.wav");
        //File wavFile = new File("/home/it210190/Music/exampleMusic/Utility-4x4-Kick.wav");
        //File wavFile = new File("/home/it210190/Music/exampleMusic/HighHopes.wav");

        // monotone
        //File wavFile = new File("/home/it210190/Music/monotone/0Hz.wav");
        //File wavFile = new File("/home/it210190/Music/monotone/49Hz.wav");
        //File wavFile = new File("/home/it210190/Music/monotone/98Hz.wav");
        //File wavFile = new File("/home/it210190/Music/monotone/988Hz.wav");

        //File wavFile = new File("/home/it210190/Music/exampleMusic/twospikes.wav");

        //File wavFile = new File("/media/it210190/UBUNTU 24_0/testlieder/120bpm_discofox_tom-gregory-footprints-2.wav");
        //File wavFile = new File("/media/it210190/UBUNTU 24_0/testlieder/168bpm_foxtrott_lemo-tu-es-2.wav");
        //File wavFile = new File("/media/it210190/UBUNTU 24_0/testlieder/172bpm_jive_footloose-kenny-loggins-2.wav");
        //File wavFile = new File("/media/it210190/UBUNTU 24_0/testlieder/44bpm_jive_bad-moon-rising-creedence-clerwater-revival-1.wav");
        File wavFile = new File("/home/tbit/Documents/testlieder/148bpm_jive_mr-brightside-the-killers-1.wav");


        double[] audioData = readWavFile(wavFile);

        Complex[] fftData = performFFT(audioData);

        stage.setTitle("Frequency Spectrum");
        final NumberAxis xAxis = new NumberAxis();
        final NumberAxis yAxis = new NumberAxis();
        xAxis.setLabel("Frequency (Hz)");
        yAxis.setLabel("Magnitude");

        final LineChart<Number, Number> lineChart = new LineChart<>(xAxis, yAxis);
        lineChart.setTitle("Frequency Spectrum");

        XYChart.Series<Number, Number> series = new XYChart.Series<>();
        series.setName("Frequency Spectrum");

        double highestMagnitude = getHighestMagnitude(fftData);

        for (int i = 0; i < fftData.length / 2000; i++) {
            double frequency = i * sampleRate / fftData.length;
            double magnitude = fftData[i].getAbs() / highestMagnitude;

            if (magnitude > 0.01) {
                series.getData().add(new XYChart.Data<>(frequency, magnitude));
            }
        }

        Complex[] fftDataLimited = new Complex[fftData.length / 2000];

        for (int i = 0; i < fftData.length / 2000; i++) {
            fftDataLimited[i] = fftData[i];
        }

        System.out.println(calculateBPM(fftDataLimited, fftData.length));



        lineChart.getData().add(series);

        Scene scene = new Scene(lineChart, 800, 600);
        stage.setScene(scene);
        stage.show();
    }

    public static double[] readWavFile(File file) throws UnsupportedAudioFileException, IOException {
        AudioInputStream audioStream = AudioSystem.getAudioInputStream(file);
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
            audioData[i] = sample / 32768.0;
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

    public static Complex[] performFFT(double[] audioData) {
    int N = audioData.length;
    if (N == 0) return new Complex[0];

    // Find the next power of 2
    int powerOf2 = 1;
    while (powerOf2 < N) {
        powerOf2 *= 2;
    }

    // Pad the audioData array with zeros
    double[] paddedAudioData = new double[powerOf2];
    System.arraycopy(audioData, 0, paddedAudioData, 0, N);

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

    public static void mapBpmToDance(){
        ArrayList<Dance> dances = initDanceTypes();

    }

    private static ArrayList<Dance> initDanceTypes(){
        ArrayList<Dance> dances = new ArrayList<>();

        Dance discofox = new Dance();
        discofox.setMinBpm(115);
        discofox.setMaxBpm(145);

        Dance foxtrott = new Dance();
        foxtrott.setMinBpm(80);
        foxtrott.setMaxBpm(115);

        Dance chacha = new Dance();
        chacha.setMinBpm(115);
        chacha.setMaxBpm(145);

        Dance jive = new Dance();
        jive.setMinBpm(115);
        jive.setMaxBpm(145);

        Dance rumba = new Dance();
        rumba.setMinBpm(115);
        rumba.setMaxBpm(145);

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