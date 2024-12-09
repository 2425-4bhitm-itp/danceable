package at.leonding.htl.features.upload;

import at.leonding.htl.features.analyze.fourier.FourierAnalysis;
import io.smallrye.mutiny.Multi;
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

import org.jboss.resteasy.annotations.providers.multipart.MultipartForm;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.ByteArrayInputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.*;
import java.util.stream.Collectors;

@Path("/upload")
public class FileUploadResource {

    @Inject
    FourierAnalysis fourierAnalysis;

    @POST
    @Consumes(MediaType.MULTIPART_FORM_DATA)
    @Produces(MediaType.APPLICATION_JSON)
    public Response getDataFromUploadedFile(
            @MultipartForm MultipartBody fileUploadBody
    ) {
        try {
            if (fileUploadBody == null || 
            fileUploadBody.file == null || 
            fileUploadBody.fileName == null
            ) {
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

    @GET
    @Path("/file")
    @Produces(MediaType.APPLICATION_JSON)
    public Response getFourierDataOfFile(
            @QueryParam("filePath") String filePath
    ) {
        try {
            File file = new File(filePath);
            InputStream stream = new FileInputStream(file);

            fourierAnalysis.calculateValues(stream);

            return Response
                    .ok(
                            fillFourierAnalysisDataDto(file)
                    )
                    .build();
        } catch (UnsupportedAudioFileException | IOException e) {
            throw new RuntimeException(e);
        }
    }

    @GET
    @Path("/inputstream")
    @Produces(MediaType.APPLICATION_JSON)
    public Response getInputstreamOfFile(
            @QueryParam("filePath") String filePath
    ) {
        try {
            File file = new File(filePath);
            InputStream stream = new FileInputStream(file);

            return Response
                    .ok(stream)
                    .build();
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }

    @GET
    @Path("/doubles")
    @Produces(MediaType.APPLICATION_JSON)
    public Response getDoubleValuesOfFile(
            @QueryParam("filePath") String filePath
    ) {
        try {
            File file = new File(filePath);
            InputStream stream = new FileInputStream(file);

            double[] values = ReadFile.readWavFile(stream);

            return Response
                    .ok(values)
                    .build();
        } catch (UnsupportedAudioFileException | IOException e) {
            throw new RuntimeException(e);
        }
    }

    @GET
    @Path("/dir")
    @Produces(MediaType.APPLICATION_JSON)
    public Response getFourierFromDirectory(
            @QueryParam("dirPath") String dirPath
    ) {
        Long startTime = System.currentTimeMillis();
        File dir = new File(dirPath);
        File[] files = dir.listFiles();

        if (files == null) {
            throw new RuntimeException("No files found in directory");
        }

        List<FourierAnalysisDataDto> fourierAnalysisDataDtos = new LinkedList<>();

        for (int i = 0; i < files.length; i++) {
            FourierAnalysisDataDto fourierAnalysisDataDto = fillFourierAnalysisDataDto(files[i]);

            if (fourierAnalysisDataDto != null) {
                System.out.println((i + 1) + ". fourier analysis is finished!");
                fourierAnalysisDataDtos.add(fourierAnalysisDataDto);
            }
        }

        Long endTime = System.currentTimeMillis();

        System.out.println((startTime - endTime) / 1000 + " seconds elapsed for analyzing " + fourierAnalysisDataDtos.size() + " out of " + files.length + " files in directory.");

        return Response
                .ok(fourierAnalysisDataDtos)
                .build();
    }

    @GET
    @Path("/dir-concurrent")
    @Produces(MediaType.APPLICATION_JSON)
    public Response getFourierFromDirectoryConcurrent(
            @QueryParam("dirPath") String dirPath
    ) {
        Long startTime = System.currentTimeMillis();
        File dir = new File(dirPath);
        File[] files = dir.listFiles();

        if (files == null) {
            throw new RuntimeException("No files found in directory");
        }

        List<FourierAnalysisDataDto> concurrentFourierAnalysisDataDtos = Collections.synchronizedList(new ArrayList<>());
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

        System.out.println((startTime - endTime) / 1000 + " seconds elapsed for analyzing " + concurrentFourierAnalysisDataDtos.size() + " out of " + files.length + " files in directory.");

        return Response
                .ok(concurrentFourierAnalysisDataDtos)
                .build();
    }

    private FourierAnalysisDataDto fillFourierAnalysisDataDto(File file) {
        return fillFourierAnalysisDataDto(file, this.fourierAnalysis);
    }

    private FourierAnalysisDataDto fillFourierAnalysisDataDto(File file, FourierAnalysis fourierAnalysis) {
        FourierAnalysisDataDto fourierAnalysisDataDto = null;

        if (
                file.isFile() &&
                        file.getName().endsWith(".wav")
        ) {
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
                        file.getName()
                );
            } catch (UnsupportedAudioFileException | IOException e) {
                throw new RuntimeException(e);
            }
        }

        return fourierAnalysisDataDto;
    }
}