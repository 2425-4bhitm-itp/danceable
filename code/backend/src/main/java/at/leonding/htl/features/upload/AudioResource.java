package at.leonding.htl.features.upload;

import at.leonding.htl.features.library.dance.Dance;
import at.leonding.htl.features.library.dance.DanceRepository;
import at.leonding.htl.features.ml.classify.ClassifyMlClient;
import at.leonding.htl.features.ml.classify.ClassifyResponse;
import at.leonding.htl.features.ml.classify.PredictionDto;
import at.leonding.htl.features.ml.classify.SpeedCategory;
import at.leonding.htl.features.ml.features.AudioFeatureClient;
import io.quarkus.logging.Log;
import jakarta.inject.Inject;
import jakarta.ws.rs.Consumes;
import jakarta.ws.rs.POST;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.core.Response;
import org.eclipse.microprofile.config.inject.ConfigProperty;
import org.eclipse.microprofile.rest.client.inject.RestClient;

import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;

@Path("/audio")
public class AudioResource {
    @ConfigProperty(name = "song-storage.path")
    String songStoragePath;

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
        String absolutePath = saveAudioFile(inputStream, "wav");

        ClassifyResponse classifyResponseDto = classifyMlClient.classify(
                absolutePath
        );

        Log.info("Classify file: ");
        Log.info(absolutePath);
        Log.info(classifyResponseDto);

        Log.info("");

        List<Dance> dances = danceRepository.findAll().list();

        if (classifyResponseDto.predictions != null) {
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

        return Response.ok().build();
    }

    @POST
    @Path("uploadWebmStream")
    @Consumes("audio/*")
    public Response uploadWebm(InputStream inputStream) throws IOException {
        String absolutePath = saveAudioFile(inputStream, "webm");

        ClassifyResponse classifyResponseDto = classifyMlClient.classifyWebm(
                absolutePath
        );

        Log.info("Classify file: ");
        Log.info(absolutePath);
        Log.info(classifyResponseDto);

        Log.info("");

        List<Dance> dances = danceRepository.findAll().list();

        if (classifyResponseDto.predictions != null) {
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

        return Response.ok().build();
    }

    @POST
    @Path("uploadWebmStream/tmp")
    @Consumes("audio/*")
    public Response uploadWebmTmp(InputStream inputStream) throws IOException {
        String absolutePath = saveAudioFile(inputStream, "webm");

//        ClassifyResponse classifyResponseDto = classifyMlClient.classifyWebm(
//                absolutePath
//        );

//        Log.info("Classify file: ");
//        Log.info(absolutePath);
//        Log.info(classifyResponseDto);

//        Log.info("");

//        List<Dance> dances = danceRepository.findAll().list();
//
//        if (classifyResponseDto.predictions != null) {
//            Set<PredictionDto> predictions = classifyResponseDto.predictions.stream()
//                    .map(p -> new PredictionDto(dances.stream()
//                            .filter(d -> d.getName().equalsIgnoreCase(p.danceName()))
//                            .map(Dance::getId)
//                            .findFirst()
//                            .orElse(null),
//                            p.confidence(),
//                            p.speedCategory())
//                    ).filter(p -> p.danceId() != null)
//                    .collect(Collectors.toSet());
        Log.info(absolutePath);
        Set<PredictionDto> predictions = new HashSet<>(Set.of(
                new PredictionDto(1L, 0.92, SpeedCategory.slow),
                new PredictionDto(2L, 0.78, SpeedCategory.medium),
                new PredictionDto(3L, 0.64, SpeedCategory.fast)
        ));

        return Response.ok().entity(predictions).build();
//        }
//
//        return Response.ok().build();
    }

    @POST
    @Path("ios/mock")
    @Consumes("audio/wave")
    public Response classifyIosMock(InputStream inputStream) throws IOException {
        Long viennaWaltzId = danceRepository.findDanceByName("viennawaltz").getId();
        Long slowWaltzId = danceRepository.findDanceByName("Slowwaltz").getId();
        Long quickstepId = danceRepository.findDanceByName("Viennawaltz").getId();

        List<PredictionDto> predictions = List.of(
                new PredictionDto(viennaWaltzId, 0.7, SpeedCategory.medium),
                new PredictionDto(slowWaltzId, 0.25, SpeedCategory.slow),
                new PredictionDto(quickstepId, 0.05, SpeedCategory.fast)
        );

        return Response.ok().entity(predictions).build();
    }

    @POST
    @Path("features")
    @Consumes("audio/wave")
    public Response extractFeatures(InputStream inputStream) throws IOException {
        String absolutePath = saveAudioFile(inputStream, "wav");

        return Response.ok().entity(
                audioFeatureClient.extractFeatures(absolutePath)
        ).build();
    }

    private String saveAudioFile(InputStream inputStream, String fileType) throws IOException {
        String audioFileLocation = "";

        if (fileType.equals("wav")) {
            audioFileLocation = songStoragePath + "/uploadedAudio_" + System.currentTimeMillis() + ".wav";
        } else if (fileType.equals("webm")) {
            audioFileLocation = songStoragePath + "/uploadedAudio_" + System.currentTimeMillis() + ".webm";
        }

        java.nio.file.Path audioFilePath = java.nio.file.Path.of(
                audioFileLocation);

        Files.copy(inputStream, audioFilePath);

        return audioFilePath.toAbsolutePath().toString();
    }
}