package at.leonding.htl.features.ml.classify;

import jakarta.ws.rs.*;
import jakarta.ws.rs.core.MediaType;
import org.eclipse.microprofile.rest.client.inject.RegisterRestClient;

@RegisterRestClient(configKey = "ml-service")
public interface ClassifyMlClient {
    @POST
    @Path("classify_audio")
    @Consumes(MediaType.APPLICATION_JSON)
    @Produces(MediaType.APPLICATION_JSON)
    ClassifyResponse classify(@QueryParam("file_path") String filePath);

    @POST
    @Path("classify_webm_audio")
    @Consumes(MediaType.APPLICATION_JSON)
    @Produces(MediaType.APPLICATION_JSON)
    ClassifyResponse classifyWebm(@QueryParam("file_path") String filePath);
}
