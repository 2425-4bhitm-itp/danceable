package at.leonding.htl.features.analyze;

public class AnalysisResult {
    private float bpm;
    private String pitch;

    public AnalysisResult(float bpm, String pitch) {
        this.bpm = bpm;
        this.pitch = pitch;
    }

    public float getBpm() {
        return bpm;
    }

    public void setBpm(float bpm) {
        this.bpm = bpm;
    }

    public String getPitch() {
        return pitch;
    }

    public void setPitch(String pitch) {
        this.pitch = pitch;
    }

    @Override
    public String toString() {
        return "AnalysisResult{" +
                "bpm=" + bpm +
                ", pitch='" + pitch + '\'' +
                '}';
    }
}