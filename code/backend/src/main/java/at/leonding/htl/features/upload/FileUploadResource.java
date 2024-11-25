package at.leonding.htl.features.upload;

import at.leonding.htl.features.analyze.fourier.FourierAnalysis;
import com.fasterxml.jackson.databind.node.JsonNodeFactory;
import com.fasterxml.jackson.databind.node.ObjectNode;
import jakarta.inject.Inject;
import jakarta.transaction.Transactional;
import jakarta.ws.rs.*;
import jakarta.ws.rs.core.MediaType;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.core.MediaType;
import jakarta.ws.rs.core.Response;
import org.jboss.resteasy.annotations.providers.multipart.MultipartForm;

import java.io.*;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;
import java.util.stream.Collectors;
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

    @GET
    @Path("/file")
    @Produces(MediaType.APPLICATION_JSON)
    public Response getFourierDataOfFile(@QueryParam("filePath") String filePath){
        try {
            File file = new File(filePath);
            InputStream stream = new FileInputStream(file);

            fourierAnalysis.calculateValues(stream);

            Map<Double, Double> frequencyMagnitudeMap = fourierAnalysis.getFrequencyMagnitudeMap();

            Map<Double, Double> filteredMap = frequencyMagnitudeMap.entrySet().stream()
                    .filter(entry -> entry.getKey() <= 5)
                    .collect(Collectors.toMap(Map.Entry::getKey, Map.Entry::getValue));

            double bpm = fourierAnalysis.getBpm();
            List<String> danceTypes = fourierAnalysis.getDanceTypes();

//            JsonNodeFactory factory = JsonNodeFactory.instance;
//            ObjectNode json = factory.objectNode();
//
//            json.put("bpm", bpm);
//            json.put("danceTypes", danceTypes.toString());
//            json.put("frequencyMagnitudeMap", filteredMap.toString());


            Map<Double, Double> sortedTreeMap = new TreeMap<>(filteredMap);


            return Response
                    .ok(
                            new FourierAnalysisDataDto(
                                    bpm, danceTypes, sortedTreeMap.keySet().toArray(new Double[0]), sortedTreeMap.values().toArray(new Double[0])
                            )
                    )
                    .build();
        } catch (UnsupportedAudioFileException | IOException e) {
            throw new RuntimeException(e);
        }
    }
}