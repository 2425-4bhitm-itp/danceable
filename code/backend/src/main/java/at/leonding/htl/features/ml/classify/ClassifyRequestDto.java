package at.leonding.htl.features.ml.classify;

import com.fasterxml.jackson.annotation.JsonProperty;

public record ClassifyRequestDto(
        @JsonProperty("file_path")
        String filePath
) {
}