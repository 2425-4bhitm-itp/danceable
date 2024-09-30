package at.leonding.htl.features.analyze;

import java.io.InputStream;

public class BPMAnalyzer {
    static {
        System.load(BPMAnalyzer.class.getResource("/libMp3Analyzer.so").getPath()); // Load the native library
    }

    // Native method declaration
    private native float analyzeBPM(InputStream audioStream);

    public float getBPM(InputStream audioStream) {
        return analyzeBPM(audioStream);
    }
}