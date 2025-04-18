package at.leonding.htl.features.upload;

import at.leonding.htl.features.ml.PythonClient;
import at.leonding.htl.features.prediction.Prediction;
import at.leonding.htl.features.prediction.PredictionDto;
import at.leonding.htl.features.prediction.PredictionRepository;
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
    PythonClient pythonClient;

    @POST
    @Path("uploadStream")
    @Consumes("audio/wave")
    public Response uploadAudioStream(InputStream inputStream) throws IOException {
        String audioFileLocation = "./uploadedAudio_" + System.currentTimeMillis() + ".wav";
        Files.copy(inputStream, java.nio.file.Path.of(
                audioFileLocation));

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