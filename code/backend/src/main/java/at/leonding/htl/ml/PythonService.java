package at.leonding.htl.ml;

import at.leonding.htl.features.analyze.fourier.FourierAnalysis;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.enterprise.event.Observes;
import jakarta.inject.Inject;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.QueryParam;
import jakarta.ws.rs.client.Client;
import jakarta.ws.rs.client.ClientBuilder;
import jakarta.ws.rs.client.Entity;
import jakarta.ws.rs.core.MediaType;
import jakarta.ws.rs.core.Response;
import jakarta.ws.rs.GET;
import jakarta.ws.rs.Path;

import io.quarkus.runtime.StartupEvent;
import io.quarkus.runtime.ShutdownEvent;

import javax.sound.sampled.UnsupportedAudioFileException;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;

@Path("/ml")
@ApplicationScoped
public class PythonService {

    private static Client client;
    final private static String pythonUrl = "http://localhost:5000/process";

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
    public String sendJson(String jsonPayload) {
        if (client == null) {
            return "Client is not initialized.";
        }
        try {
            Response response = client.target(pythonUrl)
                    .request(MediaType.APPLICATION_JSON)
                    .post(Entity.entity(jsonPayload, MediaType.APPLICATION_JSON));

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
