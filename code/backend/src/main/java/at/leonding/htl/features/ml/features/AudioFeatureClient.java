package at.leonding.htl.features.ml.features;

import jakarta.ws.rs.POST;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.QueryParam;
import jakarta.ws.rs.core.MediaType;
import org.eclipse.microprofile.rest.client.inject.RegisterRestClient;

import java.util.Map;

@RegisterRestClient
public interface AudioFeatureClient {
    @POST
    @Path("features")
    @Produces(MediaType.APPLICATION_JSON)
    Map<String, Object> extractFeatures(@QueryParam("file_path") String filePath);
}