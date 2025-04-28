package at.leonding.htl.features.upload;

import at.leonding.htl.features.ml.classify.ClassifyMlClient;
import at.leonding.htl.features.ml.classify.ClassifyRequestDto;
import at.leonding.htl.features.prediction.PredictionDto;
import at.leonding.htl.features.prediction.PredictionRepository;
import io.quarkus.logging.Log;
import jakarta.inject.Inject;
import jakarta.ws.rs.Consumes;
import jakarta.ws.rs.POST;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.core.Response;
import org.eclipse.microprofile.rest.client.inject.RestClient;

import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.util.List;

@Path("/audio")
public class AudioResource {
    @Inject
    PredictionRepository predictionRepository;

    @RestClient
    ClassifyMlClient classifyMlClient;

    @POST
    @Path("uploadStream")
    @Consumes("audio/wave")
    public Response uploadAudioStream(InputStream inputStream) throws IOException {
        String audioFileLocation = "/app/song-storage/uploadedAudio_" + System.currentTimeMillis() + ".wav";
        java.nio.file.Path audioFilePath = java.nio.file.Path.of(
                audioFileLocation);

        Files.copy(inputStream, audioFilePath);

        Log.info(audioFilePath.toAbsolutePath().toString());
        Log.info(classifyMlClient.classify(
                new ClassifyRequestDto(audioFilePath.toAbsolutePath().toString())
        ));

        List<PredictionDto> predictions = predictionRepository.listAll().stream()
                .map(p -> new PredictionDto(
                                p.getId(),
                                p.getDance().getId(),
                                p.getConfidence(),
                                p.getSpeedCategory()
                        )
                ).toList();

        return Response.ok().entity(predictions).build();
    }
}