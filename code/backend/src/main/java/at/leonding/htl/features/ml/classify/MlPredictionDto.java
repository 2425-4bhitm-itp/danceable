package at.leonding.htl.features.ml.classify;

public record MlPredictionDto(
        String danceName,
        double confidence,
        SpeedCategory speedCategory
) {
}
