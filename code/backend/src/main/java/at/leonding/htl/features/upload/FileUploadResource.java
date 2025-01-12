package at.leonding.htl.features.upload;

import at.leonding.htl.features.analyze.fourier.FourierAnalysis;
import at.leonding.htl.ml.PythonService;
import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.inject.Inject;
import jakarta.ws.rs.Consumes;
import jakarta.ws.rs.GET;
import jakarta.ws.rs.POST;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.QueryParam;
import jakarta.ws.rs.core.MediaType;
import jakarta.ws.rs.core.Response;

import javax.sound.sampled.UnsupportedAudioFileException;

import org.eclipse.microprofile.config.inject.ConfigProperty;
import org.jboss.resteasy.annotations.providers.multipart.MultipartForm;

import java.io.ByteArrayInputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.stream.Collectors;

@Path("/upload")
public class FileUploadResource {

    @ConfigProperty(name = "UPLOAD_DIRECTORY", defaultValue = "./")
    String UPLOAD_DIRECTORY;

    @Inject
    FourierAnalysis fourierAnalysis;

    @POST
    @Consumes(MediaType.MULTIPART_FORM_DATA)
    @Produces(MediaType.APPLICATION_JSON)
    public Response getDataFromUploadedFile(
            @MultipartForm MultipartBody fileUploadBody) {
        try {
            if (fileUploadBody == null ||
                    fileUploadBody.file == null ||
                    fileUploadBody.fileName == null) {
                return Response.status(Response.Status.BAD_REQUEST)
                        .entity("{\"error\": \"Invalid upload body\"}")
                        .build();
            }

            InputStream stream;

            // Check file type and process accordingly
            if (fileUploadBody.fileName.endsWith(".webm")) {
                stream = ReadFile.convertWebmToWav(
                        new ByteArrayInputStream(
                                fileUploadBody.file.readAllBytes()));
            } else if (fileUploadBody.fileName.endsWith(".wav")) {
                stream = new ByteArrayInputStream(fileUploadBody.file.readAllBytes());
            } else {
                return Response.status(Response.Status.UNSUPPORTED_MEDIA_TYPE)
                        .entity("{\"error\": \"File format not supported\"}")
                        .build();
            }

            // Perform Fourier analysis
            fourierAnalysis.calculateValues(stream);

            // Create and return the response DTO
            File tempFile = new File(fileUploadBody.fileName);
            return Response.ok(fillFourierAnalysisDataDto(tempFile)).build();
        } catch (Exception e) {
            return Response.status(Response.Status.INTERNAL_SERVER_ERROR)
                    .entity("{\"error\": \"" + e.getMessage() + "\"}")
                    .build();
        }
    }

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

    @GET
    @Path("/file")
    @Produces(MediaType.APPLICATION_JSON)
    public Response getFourierDataOfFile(
            @QueryParam("filePath") String filePath) {
        try {
            File file = new File(filePath);
            InputStream stream = new FileInputStream(file);

            fourierAnalysis.calculateValues(stream);

            // create dto make a json, stringify json and call the sendJson in PythonService, return python answer
            FourierAnalysisDataDto dto = fillFourierAnalysisDataDto(file);

            String jsonPayload = new ObjectMapper().writeValueAsString(dto);
            String pythonResponse = new PythonService().sendJson(jsonPayload);

            return Response.ok(pythonResponse).build();

        } catch (UnsupportedAudioFileException | IOException e) {
            throw new RuntimeException(e);
        }
    }

    @GET
    @Path("/dir-concurrent")
    @Produces(MediaType.APPLICATION_JSON)
    public Response getFourierFromDirectoryConcurrent(
            @QueryParam("dirPath") String dirPath) {
        Long startTime = System.currentTimeMillis();
        File dir = new File(dirPath);
        File[] files = dir.listFiles();

        if (files == null) {
            throw new RuntimeException("No files found in directory");
        }

        List<FourierAnalysisDataDto> concurrentFourierAnalysisDataDtos = Collections
                .synchronizedList(new ArrayList<>());
        List<Thread> threads = new ArrayList<>();

        for (File file : files) {
            Thread thread = new Thread(() -> {
                FourierAnalysis fourierAnalysis = new FourierAnalysis();

                FourierAnalysisDataDto fourierAnalysisDataDto = fillFourierAnalysisDataDto(file, fourierAnalysis);

                if (fourierAnalysisDataDto != null) {
                    System.out.println("A file has been fourier analyzed.");
                    concurrentFourierAnalysisDataDtos.add(fourierAnalysisDataDto);
                }
            });

            threads.add(thread);
            thread.start();
        }

        for (Thread thread : threads) {
            try {
                thread.join();
            } catch (InterruptedException e) {
                throw new RuntimeException("Error while waiting for thread completion", e);
            }
        }

        Long endTime = System.currentTimeMillis();

        System.out.println((startTime - endTime) / 1000 + " seconds elapsed for analyzing "
                + concurrentFourierAnalysisDataDtos.size() + " out of " + files.length + " files in directory.");

        return Response
                .ok(concurrentFourierAnalysisDataDtos)
                .build();
    }

    private FourierAnalysisDataDto fillFourierAnalysisDataDto(File file) {
        return fillFourierAnalysisDataDto(file, this.fourierAnalysis);
    }

    private FourierAnalysisDataDto fillFourierAnalysisDataDto(File file, FourierAnalysis fourierAnalysis) {
        FourierAnalysisDataDto fourierAnalysisDataDto = null;

        if (file.isFile() &&
                file.getName().endsWith(".wav")) {
            try {
                InputStream stream = new FileInputStream(file);

                fourierAnalysis.calculateValues(stream);

                Map<Double, Double> frequencyMagnitudeMap = fourierAnalysis.getFrequencyMagnitudeMap();

                Map<Double, Double> filteredMap = frequencyMagnitudeMap.entrySet().stream()
                        .filter(entry -> entry.getKey() <= 5)
                        .collect(Collectors.toMap(Map.Entry::getKey, Map.Entry::getValue));

                double bpm = fourierAnalysis.getBpm();
                List<String> danceTypes = fourierAnalysis.getDanceTypes();

                Map<Double, Double> sortedTreeMap = new TreeMap<>(filteredMap);

                fourierAnalysisDataDto = new FourierAnalysisDataDto(
                        bpm,
                        danceTypes,
                        sortedTreeMap
                                .keySet()
                                .toArray(
                                        new Double[0]),
                        sortedTreeMap
                                .values()
                                .toArray(new Double[0]),
                        file.getName());
            } catch (UnsupportedAudioFileException | IOException e) {
                throw new RuntimeException(e);
            }
        }

        return fourierAnalysisDataDto;
    }
}