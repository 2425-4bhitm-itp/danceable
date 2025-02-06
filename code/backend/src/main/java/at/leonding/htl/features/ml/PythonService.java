package at.leonding.htl.features.ml;

import jakarta.enterprise.context.ApplicationScoped;
import jakarta.enterprise.event.Observes;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.client.Client;
import jakarta.ws.rs.client.ClientBuilder;
import jakarta.ws.rs.client.Entity;
import jakarta.ws.rs.core.MediaType;
import jakarta.ws.rs.core.Response;
import jakarta.ws.rs.GET;
import jakarta.ws.rs.Path;

import io.quarkus.runtime.StartupEvent;
import io.quarkus.runtime.ShutdownEvent;
import org.eclipse.microprofile.config.inject.ConfigProperty;

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

    @GET
    @Produces(MediaType.APPLICATION_JSON)
    public String generateSpectrogramFromFile(String fileNameJson) {
        if (client == null) {
            return "Client is not initialized.";
        }
        pythonUrl += "spectogramFromFile";
        try {
            Response response = client.target(pythonUrl)
                    .request(MediaType.APPLICATION_JSON)
                    .post(Entity.entity(fileNameJson, MediaType.APPLICATION_JSON));

            if (response.getStatus() == 200) {
                String responseBody = response.readEntity(String.class);
                response.close();
                return responseBody;
            } else {
                response.close();
                return "Failed to contact Python backend. HTTP status: " + response.getStatus();
            }
        } catch (Exception e) {
            return "Error occurred: " + e.getMessage();
        }
    }
}
