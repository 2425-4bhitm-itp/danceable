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

    @GET
    @Path("/file")
    @Produces(MediaType.APPLICATION_JSON)
    public Response getFourierDataOfFile(
            @QueryParam("filePath") String filePath
    ) {
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

            Map<Double, Double> sortedTreeMap = new TreeMap<>(filteredMap);


            return Response
                    .ok(
                            new FourierAnalysisDataDto(
                                    bpm,
                                    danceTypes,
                                    sortedTreeMap
                                            .keySet()
                                            .toArray(
                                                    new Double[0]),
                                    sortedTreeMap
                                            .values()
                                            .toArray(new Double[0])
                            )
                    )
                    .build();
        } catch (UnsupportedAudioFileException | IOException e) {
            throw new RuntimeException(e);
        }
    }

    @GET
    @Path("/inputstream")
    @Produces(MediaType.APPLICATION_JSON)
    public Response getInputstreamOfFile(
            @QueryParam("filePath") String filePath
    ) {
        try {
            File file = new File(filePath);
            InputStream stream = new FileInputStream(file);

            return Response
                    .ok(stream)
                    .build();
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }

    @GET
    @Path("/doubles")
    @Produces(MediaType.APPLICATION_JSON)
    public Response getDoubleValuesOfFile(
            @QueryParam("filePath") String filePath
    ) {
        try {
            File file = new File(filePath);
            InputStream stream = new FileInputStream(file);

            double[] values = fourierAnalysis.readWavFile(stream);

            return Response
                    .ok(values)
                    .build();
        } catch (UnsupportedAudioFileException | IOException e) {
            throw new RuntimeException(e);
        }
    }
}