package at.leonding.htl.features.upload;

import jakarta.servlet.http.HttpServletRequest;
import jakarta.ws.rs.Consumes;
import jakarta.ws.rs.POST;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.core.Context;
import jakarta.ws.rs.core.MediaType;
import jakarta.ws.rs.core.Response;
import org.apache.commons.io.IOUtils;
import org.jboss.resteasy.annotations.providers.multipart.MultipartForm;

import java.io.*;
import java.net.http.HttpRequest;
import java.nio.file.Files;

@Path("/audio")
public class AudioResource {

    private static final String UPLOAD_DIR = "/tmp/uploads/";

    /* Legacy upload Route (never worked anyways)
    @POST
    @Path("upload")
    @Consumes(MediaType.MULTIPART_FORM_DATA)
    @Produces(MediaType.TEXT_PLAIN)
    public Response uploadAudio(@MultipartForm AudioForm form) {
        if (form.fileData == null || form.fileName == null || form.fileName.isEmpty()) {
            return Response.status(Response.Status.BAD_REQUEST).entity("Invalid file upload request").build();
        }

        File uploadDir = new File(UPLOAD_DIR);
        if (!uploadDir.exists()) {
            uploadDir.mkdirs();
        }

        File file = new File(UPLOAD_DIR + form.fileName);
        try (FileOutputStream fos = new FileOutputStream(file)) {
            fos.write(form.fileData);
        } catch (IOException e) {
            return Response.serverError().entity("File upload failed: " + e.getMessage()).build();
        }

        return Response.ok("File uploaded successfully: " + file.getAbsolutePath()).build();
    }
    */

    @POST
    @Path("uploadStream")
    public Response uploadAudioStream(@Context HttpServletRequest request) throws IOException {
        OutputStream outStream = new FileOutputStream(new File("/src/main/resources/uploadedAudio.wav"));
        outStream.write(request.getInputStream().readAllBytes());
        outStream.close();
        return Response.ok("File uploaded successfully").build();
    }

}