package at.leonding.htl.features.ml.classify;

public record ClassifyResponseDto(
        PythonPredictionDto[] predictions
) {}
