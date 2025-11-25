package at.leonding.htl.features.ml.features;

import jakarta.ws.rs.POST;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.QueryParam;
import jakarta.ws.rs.core.MediaType;
import org.eclipse.microprofile.rest.client.inject.RegisterRestClient;

@RegisterRestClient(configKey = "ml-service")
public interface AudioFeatureClient {
    @POST
    @Path("features")
    @Produces(MediaType.APPLICATION_JSON)
    Double[] extractFeatures(@QueryParam("file_path") String filePath);
}