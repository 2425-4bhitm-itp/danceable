package at.leonding.htl.features.library;

import at.leonding.htl.features.library.songsnippet.SongSnippetRepository;
import at.leonding.htl.features.library.dance.Dance;
import at.leonding.htl.features.library.dance.DanceRepository;
import at.leonding.htl.features.library.song.Song;
import at.leonding.htl.features.library.song.SongRepository;
import io.quarkus.logging.Log;
import jakarta.inject.Inject;
import jakarta.transaction.Transactional;
import jakarta.ws.rs.*;
import jakarta.ws.rs.core.MediaType;
import jakarta.ws.rs.core.Response;
import org.eclipse.microprofile.config.inject.ConfigProperty;

import java.io.File;
import java.io.IOException;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;

@Path("/library")
@Produces(MediaType.APPLICATION_JSON)
public class LibraryResource {

    @ConfigProperty(name = "song.storage.directory")
    String songStorageDirectoryPath;

    @Inject
    DanceRepository danceRepository;

    @Inject
    SongRepository songRepository;

    @Inject
    SongSnippetRepository songSnippetRepository;

    @POST
    @Path("/feedin")
    @Transactional
    public Response feedInSongSnippetFiles(
            @QueryParam("pathName") String songStorage
    ) {
        if (songStorage == null || songStorage.isBlank()) {
            songStorage = songStorageDirectoryPath;
        }

        List<File> files = getWavFilesInDirectory(songStorage + "/feedin");

        if (files != null) {
            for (File file : files) {
                try {
                    this.moveFile(songStorage + "/library", file);
                    this.feedInSongSnippetFile(file);
                }
                catch (IOException e) {
                    Log.error("File ("
                            + file.getName()
                            + ") can not be moved: "
                            + e.getMessage()
                    );
                }
                catch (IllegalArgumentException e) {
                    Log.error(
                            "File ("
                                    + file.getName()
                                    + ") does not correspond to naming convention: "
                                    + e.getMessage()
                    );
                }
            }
        }

        return Response.ok().build();
    }

    private List<File> getWavFilesInDirectory(String directoryPath) {
        List<File> files = null;
        File[] filesArray = (new File(directoryPath)).listFiles();

        if (filesArray != null) {
            files = Arrays.stream(filesArray).toList().stream()
                    .filter(f -> f.getName().endsWith(".wav"))
                    .toList();
        }

        return files;
    }

    private Set<Dance> persistOrUpdateDances(Set<String> danceNames) {
        Set<Dance> dances = new HashSet<>();

        for (String danceName : danceNames) {
            dances.add(danceRepository.persistOrUpdateSong(danceName));
        }

        return dances;
    }

    private void feedInSongSnippetFile(File file) throws IllegalArgumentException {
        String fileName = file.getName();
        String[] fileNameSplit = fileName.split("_");

        if (fileNameSplit.length == 3) {
            int speedInBpm = Integer.parseInt(fileNameSplit[0].substring(0, fileNameSplit[0].length() - 3));
            Set<String> danceNames = Set.of(fileNameSplit[1].split("-"));

            String[] songNameArray = fileNameSplit[2].split("-");

            String songName = Arrays.stream(songNameArray)
                    .limit(songNameArray.length - 1)
                    .collect(Collectors.joining(" "));

            int songSnippetIndex = Integer.parseInt(
                    songNameArray[songNameArray.length - 1].substring(
                            0, songNameArray[songNameArray.length - 1].length() - 4
                    )
            );

            Set<Dance> dances = this.persistOrUpdateDances(danceNames);

            Song song = songRepository.persistOrUpdateSong(songName, speedInBpm, dances.stream().findFirst().orElse(null));

            songSnippetRepository.persistOrUpdateSongSnippet(
                    song, songSnippetIndex, fileName
            );
        } else {
            throw new IllegalArgumentException(fileName);
        }
    }

    private void moveFile(String directoryPath, File file) throws IOException {
        File destination = new File(directoryPath);
        if (!file.renameTo(new File(destination, file.getName()))) {
            throw new IOException("Failed to move file to " + directoryPath);
        }
    }
}