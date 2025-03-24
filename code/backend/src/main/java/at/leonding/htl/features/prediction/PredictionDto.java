package at.leonding.htl.features.prediction;

public record PredictionDto(
        Long id,
        Long danceId,
        double confidence,
        SpeedCategory speedCategory
) {
}
