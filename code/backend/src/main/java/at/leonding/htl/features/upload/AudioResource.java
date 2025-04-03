package at.leonding.htl.features.upload;

import jakarta.ws.rs.Consumes;
import jakarta.ws.rs.POST;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.core.Response;

import java.io.*;
import java.nio.file.Files;
import java.time.LocalDateTime;

@Path("/audio")
public class AudioResource {
    @POST
    @Path("uploadStream")
    @Consumes("audio/wave")
    public Response uploadAudioStream(InputStream inputStream) throws IOException {
        Files.copy(inputStream, java.nio.file.Path.of("./uploadedAudio" + LocalDateTime.now().hashCode() + ".wav"));//        OutputStream outStream = new FileOutputStream("./uploadedAudio" + LocalDate.now().hashCode() + ".wav");

        return Response.ok("File uploaded successfully").build();
    }
}