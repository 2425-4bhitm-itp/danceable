package at.leonding.htl.features.upload;

import at.leonding.htl.features.analyze.AudioAnalyzer;
import jakarta.inject.Inject;
import jakarta.ws.rs.Consumes;
import jakarta.ws.rs.POST;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.core.Response;
import org.jboss.resteasy.annotations.providers.multipart.MultipartForm;

import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Paths;

@Path("/upload")
public class FileUploadResource {

    @Inject
    AudioAnalyzer audioAnalyzer;  // Inject the analyzer

    @POST
    @Consumes("multipart/form-data")
    public Response uploadFile(@MultipartForm MultipartBody data) {
        try {
            java.nio.file.Path tempFile = Files.createTempFile("uploaded-", ".mp3");
            Files.copy(data.file, tempFile, java.nio.file.StandardCopyOption.REPLACE_EXISTING);

            // Call the analysis and save it to the database
            audioAnalyzer.analyzeAndSave(tempFile.toString(), data.fileName);

            // get the category of the uploaded file
            //String category = audioAnalyzer.categorize(tempFile.toString());

            Files.delete(tempFile); // Clean up the temporary file

            return Response.ok("File uploaded and analyzed successfully").build();
            //return Response.ok("You should dance " + category).build();
        } catch (IOException e) {
            e.printStackTrace();
            return Response.status(Response.Status.INTERNAL_SERVER_ERROR)
                    .entity("File upload failed").build();
        }
    }
}
