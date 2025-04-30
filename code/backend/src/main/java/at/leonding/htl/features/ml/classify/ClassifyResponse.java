package at.leonding.htl.features.ml.classify;

import com.fasterxml.jackson.annotation.JsonProperty;

import java.util.List;

public class ClassifyResponse {
    @JsonProperty("predictions")
    public List<MlPredictionDto> predictions;
}
