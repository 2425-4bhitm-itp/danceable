package at.leonding.htl.features.upload;

import java.io.BufferedInputStream;
import java.io.IOException;
import java.io.InputStream;

import javax.sound.sampled.AudioFormat;
import javax.sound.sampled.AudioInputStream;
import javax.sound.sampled.AudioSystem;
import javax.sound.sampled.UnsupportedAudioFileException;

public class ReadFile {

    // convert webm file to wav file
    public static InputStream convertWebmToWav(InputStream inputStream) throws IOException {
        ProcessBuilder processBuilder = new ProcessBuilder("ffmpeg", "-i", "pipe:0", "-f", "wav", "pipe:1");
        processBuilder.redirectErrorStream(true);
        Process process = processBuilder.start();

        Thread inputThread = new Thread(() -> {
            try {
                byte[] buffer = new byte[1024];
                int bytesRead;
                while ((bytesRead = inputStream.read(buffer)) != -1) {
                    process.getOutputStream().write(buffer, 0, bytesRead);
                }
                process.getOutputStream().close();
            } catch (IOException e) {
                throw new RuntimeException(e);
            }
        });
        inputThread.start();

        return process.getInputStream();
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
}