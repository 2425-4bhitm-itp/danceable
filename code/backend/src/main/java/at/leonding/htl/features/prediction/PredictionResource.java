
package at.leonding.htl.features.prediction;

import at.leonding.htl.features.ml.PythonResource;
import jakarta.inject.Inject;
import jakarta.ws.rs.GET;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.core.MediaType;
import jakarta.ws.rs.core.Response;

import java.io.InputStream;
import java.nio.file.Files;
import java.time.LocalDateTime;
import java.util.List;

@Path("/predictions")
@Produces(MediaType.APPLICATION_JSON)
public class PredictionResource {
    @Inject
    PredictionRepository predictionRepository;

    @Inject
    PythonResource pythonService;

    @GET
    public List<PredictionDto> getAllPredictions() {
        return predictionRepository.listAll().stream()
                .map(p -> new PredictionDto(
                                p.getId(),
                                p.getDance().getId(),
                                p.getConfidence(),
                                p.getSpeedCategory()
                        )
                ).toList();
    }

//    @GET
//    @Path("audio")
//    public Response getPredictionsForAudio(InputStream inputStream) {
//        try {
//            Files.copy(inputStream, java.nio.file.Path.of("./uploadedAudio" + LocalDateTime.now().hashCode() + ".wav"));//        OutputStream outStream = new FileOutputStream("./uploadedAudio" + LocalDate.now().hashCode() + ".wav");
//
//            pythonService.classifyAudio()
//
//            return Response.ok().entity().build();
//        } catch (Exception e) {
//            return Response.ok().build();
//        }
//    }
}
