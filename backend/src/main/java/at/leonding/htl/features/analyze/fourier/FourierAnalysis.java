package at.leonding.htl.features.analyze.fourier;

import javafx.application.Application;
import javafx.scene.Scene;
import javafx.scene.chart.LineChart;
import javafx.scene.chart.NumberAxis;
import javafx.scene.chart.XYChart;
import javafx.stage.Stage;

import javax.sound.sampled.*;
import java.io.File;
import java.io.IOException;

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
        File wavFile = new File("/home/it210190/Music/exampleMusic/HighHopes.wav");

        // monotone
        //File wavFile = new File("/home/it210190/Music/monotone/0Hz.wav");
        //File wavFile = new File("/home/it210190/Music/monotone/49Hz.wav");
        //File wavFile = new File("/home/it210190/Music/monotone/98Hz.wav");
        //File wavFile = new File("/home/it210190/Music/monotone/988Hz.wav");

        //File wavFile = new File("/home/it210190/Music/exampleMusic/twospikes.wav");

        double[] audioData = readWavFile(wavFile);

        Complex[] fftData = performDFT(audioData);

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

        for (int i = 0; i < fftData.length / 2; i++) {
            double frequency = i * sampleRate / fftData.length;
            double magnitude = fftData[i].getAbs() / highestMagnitude;

            if (magnitude > 0.01) {
                series.getData().add(new XYChart.Data<>(frequency, magnitude));
            }
        }
        System.out.println(highestMagnitude);
        System.out.println(calculateBPM(fftData, bpmPoints));

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
        int peakIndex = getPeakIndex(fftData);

        double bpmFrequency = peakIndex * sampleRate / pointsToCalculate;

        return bpmFrequency * 60;
    }

    public double getHighestMagnitude(Complex[] fftData) {
        int peakIndex = getPeakIndex(fftData);
        return fftData[peakIndex].getAbs();
    }
}