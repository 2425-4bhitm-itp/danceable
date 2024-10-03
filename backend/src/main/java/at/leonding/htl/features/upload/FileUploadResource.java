package at.leonding.htl.features.upload;

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

    @POST
    @Consumes("multipart/form-data")
    public Response uploadFile(@MultipartForm MultipartBody data) {
        try (InputStream uploadedFileStream = data.file) {
            java.nio.file.Path path = Paths.get("/Users/samuelmayer/Desktop/tmp", data.fileName + ".mp3");

            Files.copy(uploadedFileStream, path);
            return Response.ok("File uploaded successfully").build();
        } catch (IOException e) {
            e.printStackTrace();
            return Response.status(Response.Status.INTERNAL_SERVER_ERROR)
                           .entity("File upload failed").build();
        }
    }
}
