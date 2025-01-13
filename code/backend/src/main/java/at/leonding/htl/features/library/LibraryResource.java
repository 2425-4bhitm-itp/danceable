package at.leonding.htl.features.library;

import at.leonding.htl.features.library.audiofile.SongSnippet;
import at.leonding.htl.features.library.audiofile.SongSnippetRepository;
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

import java.io.File;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;

@Path("/library")
@Produces(MediaType.APPLICATION_JSON)
public class LibraryResource {
    private static final String DEFAULT_LIBRARY_DIRECTORY_NAME = "/app/song-storage"; // for prod in (volume)

    @Inject
    DanceRepository danceRepository;

    @Inject
    SongRepository songRepository;

    @Inject
    SongSnippetRepository songSnippetRepository;

    @POST
    @Path("/feedin")
    @Transactional
    public Response feedInAudioFiles(
            @QueryParam("pathName") @DefaultValue(DEFAULT_LIBRARY_DIRECTORY_NAME) String libraryFilePath
    ) {
        List<File> files = getWavFilesInDirectory(libraryFilePath);

        if (files != null) {
            for (File file : files) {
                try {
                    this.parseFileNameToFeedIn(file.getName());
                } catch (Exception e) {
                    Log.error(
                            "Wav file ("
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

    private void parseFileNameToFeedIn(String fileName) throws Exception {
        String[] fileNameSplit = fileName.split("_");

        if (fileNameSplit.length == 3) { // naming convention: 00bpm_dancestyleA-dancestyleB_song-name-indexX.wav
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

            Song song = songRepository.persistOrUpdateSong(songName);

            SongSnippet songSnippet = songSnippetRepository.persistOrUpdateSongSnippet(
                    song, songSnippetIndex, speedInBpm, dances, fileName
            );

            Log.info(songSnippet);
        } else {
            throw new Exception(fileName);
        }
    }
}
