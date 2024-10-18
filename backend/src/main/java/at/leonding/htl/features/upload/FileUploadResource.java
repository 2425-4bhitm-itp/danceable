package at.leonding.htl.features.upload;

import at.leonding.htl.features.analyze.AudioFeatureExtractor;
import at.leonding.htl.features.analyze.MusicFeatureService;
import jakarta.inject.Inject;
import jakarta.transaction.Transactional;
import jakarta.ws.rs.Consumes;
import jakarta.ws.rs.POST;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.core.Response;
import org.jboss.resteasy.annotations.providers.multipart.MultipartForm;

import java.util.HashMap;
import java.util.Map;
import java.util.logging.Level;
import java.util.logging.Logger;

@Path("/upload")
public class FileUploadResource {

    @Inject
    MusicFeatureService musicFeatureService;

    @Inject
    AudioFeatureExtractor audioFeatureExtractor;  // Use AudioFeatureExtractor for feature extraction

    private static final Logger LOGGER = Logger.getLogger(FileUploadResource.class.getName());

    @POST
    @Consumes("multipart/form-data")
    @Transactional
    public Response uploadFile(@MultipartForm MultipartBody data) {
        // Extract features from the uploaded audio file using AudioFeatureExtractor
        double[] features = audioFeatureExtractor.extractFeatures(data.file);

        if (features == null) {
            LOGGER.log(Level.SEVERE, "Feature extraction failed, features array is null");
            return Response.status(Response.Status.INTERNAL_SERVER_ERROR).entity("Feature extraction failed").build();
        }

        // Save features with the provided genre
        musicFeatureService.saveFeatureVector(features, data.fileName);

        // Prepare response data
        Map<String, Object> responseData = new HashMap<>();
        responseData.put("genre", data.fileName);
        responseData.put("featureVector", features);

        return Response.ok(responseData).build();
    }
}