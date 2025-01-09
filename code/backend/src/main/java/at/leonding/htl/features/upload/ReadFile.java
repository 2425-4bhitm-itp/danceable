package at.leonding.htl.features.upload;

import javax.sound.sampled.*;
import java.io.*;

public class ReadFile {


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

    public static InputStream convertWebmToWav(ByteArrayInputStream byteArrayInputStream) {
        try {
            File tempFile = File.createTempFile("temp", ".webm");
            FileOutputStream fileOutputStream = new FileOutputStream(tempFile);
            byteArrayInputStream.transferTo(fileOutputStream);
            fileOutputStream.close();

            ProcessBuilder processBuilder = new ProcessBuilder("ffmpeg", "-i", tempFile.getAbsolutePath(), "-f", "wav", "-");
            Process process = processBuilder.start();
            return process.getInputStream();
        } catch (IOException e) {
            e.printStackTrace();
            return null;
        }
    }
}