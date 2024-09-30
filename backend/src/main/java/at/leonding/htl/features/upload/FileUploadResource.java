package at.leonding.htl.features.upload;

import at.leonding.htl.features.analyze.BPMAnalyzer;
import jakarta.ws.rs.Consumes;
import jakarta.ws.rs.POST;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.core.Response;
import org.jboss.resteasy.annotations.providers.multipart.MultipartForm;

import java.io.IOException;
import java.nio.file.Files;

@Path("/upload")
public class FileUploadResource {

    @POST
    @Consumes("multipart/form-data")
    public Response uploadFile(@MultipartForm MultipartBody data) {
        try {
            java.nio.file.Path tempFile = Files.createTempFile("uploaded-", ".mp3");
            Files.copy(data.file, tempFile, java.nio.file.StandardCopyOption.REPLACE_EXISTING);

            BPMAnalyzer bpmAnalyzer = new BPMAnalyzer();
            float bpm = bpmAnalyzer.getBPM(tempFile.toString());
            System.out.println("BPM: " + bpm);

            Files.delete(tempFile); // Clean up the temporary file

            return Response.ok("File uploaded successfully").build();
        } catch (IOException e) {
            e.printStackTrace();
            return Response.status(Response.Status.INTERNAL_SERVER_ERROR)
                           .entity("File upload failed").build();
        }
    }
}