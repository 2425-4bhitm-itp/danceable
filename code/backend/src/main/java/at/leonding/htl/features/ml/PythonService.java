package at.leonding.htl.features.ml;

import at.leonding.htl.features.upload.MultipartBody;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.enterprise.event.Observes;
import jakarta.ws.rs.*;
import jakarta.ws.rs.client.Client;
import jakarta.ws.rs.client.ClientBuilder;
import jakarta.ws.rs.client.Entity;
import jakarta.ws.rs.core.MediaType;
import jakarta.ws.rs.core.Response;

import io.quarkus.runtime.StartupEvent;
import io.quarkus.runtime.ShutdownEvent;
import org.eclipse.microprofile.config.inject.ConfigProperty;
import org.jboss.resteasy.annotations.providers.multipart.MultipartForm;

import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Paths;

@Path("/ml")
@ApplicationScoped
public class PythonService {

    private static Client client;

    @ConfigProperty(name = "ML_URL", defaultValue = "http://ml:5001/")
    String pythonUrl;

    void onStart(@Observes StartupEvent ev) {
        client = ClientBuilder.newClient();
        System.out.println("Application started");
    }

    void onStop(@Observes ShutdownEvent ev) {
        client.close();
        System.out.println("Application stopped");
    }

    @POST
    @Path("/process_and_train")
    public Response processAndTrain() {
        try {
            // Process all WAV files
            Response response = client.target(pythonUrl + "processing_wav")
                                      .request()
                                      .post(null);
            if (response.getStatus() != 200) {
                return Response.status(Response.Status.INTERNAL_SERVER_ERROR)
                               .entity("Error processing WAV files")
                               .build();
            }

            // Create CSV
            response = client.target(pythonUrl + "process_all_audio")
                             .request()
                             .post(null);
            if (response.getStatus() != 200) {
                return Response.status(Response.Status.INTERNAL_SERVER_ERROR)
                               .entity("Error creating CSV")
                               .build();
            }

            // Train model
            response = client.target(pythonUrl + "train")
                             .request()
                             .get();
            if (response.getStatus() != 200) {
                return Response.status(Response.Status.INTERNAL_SERVER_ERROR)
                               .entity("Error training model")
                               .build();
            }

            return Response.ok("Processing and training completed successfully").build();
        } catch (Exception e) {
            return Response.status(Response.Status.INTERNAL_SERVER_ERROR)
                           .entity("An error occurred: " + e.getMessage())
                           .build();
        }
    }

    @POST
    @Path("/classify_audio")
    @Consumes(MediaType.MULTIPART_FORM_DATA)
    public Response classifyAudio(@MultipartForm MultipartBody multipartBody) {
        if (multipartBody.fileName == null || multipartBody.fileName.isEmpty()) {
            return Response.status(Response.Status.BAD_REQUEST)
                    .entity("{\"error\":\"File name is required.\"}")
                    .build();
        }

        try {
            String uploadedFileLocation = "/tmp/" + multipartBody.fileName;
            java.nio.file.Path target = Paths.get(uploadedFileLocation);

            Files.copy(multipartBody.file, target);

            String json = "{\"file\": \"" + uploadedFileLocation + "\"}";

            Response response = null;

            if (uploadedFileLocation.endsWith(".webm")) {
                response = client.target(pythonUrl + "classify_webm_audio")
                        .request()
                        .post(Entity.entity(json, MediaType.APPLICATION_JSON));
            } else if (uploadedFileLocation.endsWith(".wav")) {
                response = client.target(pythonUrl + "classify_audio")
                        .request()
                        .post(Entity.entity(json, MediaType.APPLICATION_JSON));
            }

            Files.delete(target);

            return Response.status(response.getStatus())
                    .entity(response.readEntity(String.class))
                    .build();
        } catch (Exception e) {
            return Response.status(Response.Status.INTERNAL_SERVER_ERROR)
                    .entity("An error occurred: " + e.getMessage())
                    .build();
        }
    }
}
