package at.leonding.htl.features.analyze;

public class BPMAnalyzer {
    static {
        System.load(BPMAnalyzer.class.getResource("/libMp3Analyzer.so").getPath()); // Load the native library
    }

    // Native method declaration
    private native float analyzeBPM(String filePath);

    public float getBPM(String filePath) {
        return analyzeBPM(filePath);
    }
}