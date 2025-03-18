package at.leonding.htl.features.upload;

import at.leonding.htl.features.ml.PythonService;

import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.inject.Inject;
import jakarta.ws.rs.Consumes;
import jakarta.ws.rs.POST;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.core.MediaType;
import jakarta.ws.rs.core.Response;

import org.eclipse.microprofile.config.inject.ConfigProperty;
import org.jboss.resteasy.annotations.providers.multipart.MultipartForm;

import java.io.*;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;

@Path("/upload")
public class FileUploadResource {

    @ConfigProperty(name = "UPLOAD_DIRECTORY", defaultValue = "./")
    String UPLOAD_DIRECTORY;

    @Inject
    PythonService pythonService;

    @Path("/save")
    @POST
    @Consumes(MediaType.MULTIPART_FORM_DATA)
    @Produces(MediaType.APPLICATION_JSON)
    public Response saveAudioFile(@MultipartForm MultipartBody multipartBody) {
        if (multipartBody.fileName == null || multipartBody.fileName.isEmpty()) {
            return Response.status(Response.Status.BAD_REQUEST)
                    .entity("{\"error\":\"File name is required.\"}")
                    .build();
        }

        InputStream uploadedInputStream = multipartBody.file;
        String uploadedFileName = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd-HH-ss")) + "_"
                + multipartBody.fileName;

        File outputFile = new File(UPLOAD_DIRECTORY, uploadedFileName);

        try (FileOutputStream outStream = new FileOutputStream(outputFile)) {
            byte[] buffer = new byte[1024];
            int bytesRead;

            while ((bytesRead = uploadedInputStream.read(buffer)) != -1) {
                outStream.write(buffer, 0, bytesRead);
            }

            List<String> cmds = new ArrayList<>();
            cmds.add("ffmpeg");
            cmds.add("-i");
            cmds.add(outputFile.getAbsolutePath());
            cmds.add(UPLOAD_DIRECTORY + "/" + uploadedFileName.split("\\.")[0] + ".wav");

            ProcessBuilder pb = new ProcessBuilder(cmds);
            Process p = pb.start();
            p.waitFor();

            return Response.ok().build();
        } catch (IOException e) {
            return Response.status(Response.Status.INTERNAL_SERVER_ERROR).build();
        } catch (InterruptedException e) {
            throw new RuntimeException(e);
        }
    }
}