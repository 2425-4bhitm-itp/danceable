package at.leonding.htl.features.upload;

import at.leonding.htl.features.analyze.fourier.FourierAnalysis;
import com.fasterxml.jackson.databind.node.JsonNodeFactory;
import com.fasterxml.jackson.databind.node.ObjectNode;
import jakarta.inject.Inject;
import jakarta.transaction.Transactional;
import jakarta.ws.rs.Consumes;
import jakarta.ws.rs.POST;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.core.MediaType;
import jakarta.ws.rs.core.Response;
import org.jboss.resteasy.annotations.providers.multipart.MultipartForm;

import java.io.File;
import java.io.IOException;
import java.util.List;
import java.util.Map;
import javax.sound.sampled.UnsupportedAudioFileException;

@Path("/upload")
public class FileUploadResource {

    @Inject
    FourierAnalysis fourierAnalysis;

    @POST
    @Consumes("multipart/form-data")
    @Produces(MediaType.APPLICATION_JSON)
    @Transactional
    public Response uploadFile(@MultipartForm MultipartBody data) {
        try {
            fourierAnalysis.calculateValues(data.file);

            Map<Double, Double> frequencyMagnitudeMap = fourierAnalysis.getFrequencyMagnitudeMap();
            double bpm = fourierAnalysis.getBpm();
            List<String> danceTypes = fourierAnalysis.getDanceTypes();

            JsonNodeFactory factory = JsonNodeFactory.instance;
            ObjectNode json = factory.objectNode();

            json.put("bpm", bpm);
            json.put("danceTypes", danceTypes.toString());
            json.put("frequencyMagnitudeMap", frequencyMagnitudeMap.toString());

            return Response
                    .ok(json)
                    .build();
        } catch (UnsupportedAudioFileException | IOException e) {
            e.printStackTrace();
            return Response
                    .status(Response.Status.INTERNAL_SERVER_ERROR)
                    .entity("Error processing file").build();
        }
    }
}