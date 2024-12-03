package at.leonding.htl.features.upload;

import java.util.List;

public record FourierAnalysisDataDto(
        double bpm,
        List<String> danceTypes,
        Double[] frequencies,
        Double[] magnitudes,
        String fileName
) {
}
