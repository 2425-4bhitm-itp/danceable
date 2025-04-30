package at.leonding.htl.features.upload;

import at.leonding.htl.features.library.dance.Dance;
import at.leonding.htl.features.library.dance.DanceRepository;
import at.leonding.htl.features.ml.classify.ClassifyMlClient;
import at.leonding.htl.features.ml.classify.ClassifyResponse;
import at.leonding.htl.features.ml.classify.PredictionDto;
import at.leonding.htl.features.ml.features.AudioFeatureClient;
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
import java.util.Set;
import java.util.stream.Collectors;

@Path("/audio")
public class AudioResource {
    @Inject
    DanceRepository danceRepository;

    @RestClient
    ClassifyMlClient classifyMlClient;

    @RestClient
    AudioFeatureClient audioFeatureClient;

    @POST
    @Path("uploadStream")
    @Consumes("audio/wave")
    public Response uploadAudioStream(InputStream inputStream) throws IOException {
        String absolutePath = saveAudioFile(inputStream);

        ClassifyResponse classifyResponseDto = classifyMlClient.classify(
                absolutePath
        );

        Log.info("Classify file: ");
        Log.info(absolutePath);
        Log.info(classifyResponseDto);

        List<Dance> dances = danceRepository.findAll().list();

        Set<PredictionDto> predictions = classifyResponseDto.predictions.stream()
                .map(p -> new PredictionDto(dances.stream()
                        .filter(d -> d.getName().equalsIgnoreCase(p.danceName()))
                        .map(Dance::getId)
                        .findFirst()
                        .orElse(null),
                        p.confidence(),
                        p.speedCategory())
                ).filter(p -> p.danceId() != null)
                .collect(Collectors.toSet());

        return Response.ok().entity(predictions).build();
    }

    @POST
    @Path("features")
    @Consumes("audio/wave")
    public Response extractFeatures(InputStream inputStream) throws IOException {
        String absolutePath = saveAudioFile(inputStream);

        return Response.ok().entity(
                audioFeatureClient.extractFeatures(absolutePath)
        ).build();
    }

    private String saveAudioFile(InputStream inputStream) throws IOException {
        String audioFileLocation = "/app/song-storage/uploadedAudio_" + System.currentTimeMillis() + ".wav";
        java.nio.file.Path audioFilePath = java.nio.file.Path.of(
                audioFileLocation);

        Files.copy(inputStream, audioFilePath);

        return audioFilePath.toAbsolutePath().toString();
    }
}