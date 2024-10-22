package at.leonding.htl.features.upload;

import jakarta.inject.Inject;
import jakarta.transaction.Transactional;
import jakarta.ws.rs.Consumes;
import jakarta.ws.rs.POST;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.core.Response;
import org.jboss.resteasy.annotations.providers.multipart.MultipartForm;

import java.time.Duration;
import java.time.Instant;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.logging.Level;
import java.util.logging.Logger;

@Path("/upload")
public class FileUploadResource {

    @POST
    @Consumes("multipart/form-data")
    @Transactional
    public Response uploadFile(@MultipartForm MultipartBody data) {


        return Response.ok("").build();
    }
}