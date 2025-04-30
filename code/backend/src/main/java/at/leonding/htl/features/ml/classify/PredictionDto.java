
package at.leonding.htl.features.ml.classify;

public record PredictionDto(
        Long danceId,
        double confidence,
        SpeedCategory speedCategory
) {
}
