package at.leonding.htl.features.prediction;

import jakarta.inject.Inject;
import jakarta.ws.rs.GET;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.core.MediaType;

import java.util.List;

@Path("/predictions")
@Produces(MediaType.APPLICATION_JSON)
public class PredictionResource {
    @Inject
    PredictionRepository predictionRepository;

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
}
