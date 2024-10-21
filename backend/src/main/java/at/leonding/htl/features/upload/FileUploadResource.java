package at.leonding.htl.features.upload;

import at.leonding.htl.features.analyze.fourier.AudioFeatureExtractor;
import at.leonding.htl.features.analyze.fourier.MusicFeatureService;
import jakarta.inject.Inject;
import jakarta.transaction.Transactional;
import jakarta.ws.rs.Consumes;
import jakarta.ws.rs.POST;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.core.Response;
import org.jboss.resteasy.annotations.providers.multipart.MultipartForm;

import java.time.Duration;
import java.time.Instant;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.logging.Level;
import java.util.logging.Logger;

@Path("/upload")
public class FileUploadResource {

    @Inject
    MusicFeatureService musicFeatureService;

    @Inject
    AudioFeatureExtractor audioFeatureExtractor;

    private static final Logger LOGGER = Logger.getLogger(FileUploadResource.class.getName());

    @POST
    @Consumes("multipart/form-data")
    @Transactional
    public Response uploadFile(@MultipartForm MultipartBody data) {
        Instant start = Instant.now();

        System.out.println("Received file: " + data.fileName);
        // Step 1: Extract features from the uploaded audio file
        Instant featureStart = Instant.now();
        List<Double> features = audioFeatureExtractor.extractFeatures(data.file);
        Instant featureEnd = Instant.now();
        LOGGER.log(Level.INFO, "Feature extraction time: " + Duration.between(featureStart, featureEnd).toMillis() + " ms");

        if (features == null) {
            LOGGER.log(Level.SEVERE, "Feature extraction failed, features array is null");
            return Response.status(Response.Status.INTERNAL_SERVER_ERROR).entity("Feature extraction failed").build();
        }

        // Step 2: Save features with the provided genres
        Instant saveStart = Instant.now();
        musicFeatureService.saveFeatureVector(features, data.fileName);
        Instant saveEnd = Instant.now();
        LOGGER.log(Level.INFO, "Database save time: " + Duration.between(saveStart, saveEnd).toMillis() + " ms");

        // Step 3: Prepare response data
        Map<String, Object> responseData = new HashMap<>();
        responseData.put("genres", data.fileName.split(","));
        responseData.put("featureVector", features);

        Instant end = Instant.now();
        LOGGER.log(Level.INFO, "Total upload time: " + Duration.between(start, end).toMillis() + " ms");

        return Response.ok(responseData).build();
    }
}