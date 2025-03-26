package at.leonding.htl.features.library.song;

import at.leonding.htl.features.library.dance.Dance;
import at.leonding.htl.features.library.dance.DanceRepository;
import jakarta.inject.Inject;
import jakarta.transaction.Transactional;
import jakarta.ws.rs.GET;
import jakarta.ws.rs.POST;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.core.MediaType;
import jakarta.ws.rs.core.Response;

import java.util.List;
import java.util.stream.Collectors;

@Path("/songs")
@Produces(MediaType.APPLICATION_JSON)
public class SongResource {
    @Inject
    SongRepository songRepository;

    @Inject
    DanceRepository danceRepository;

    @GET
    public List<SongDto> getAllSongs() {
        return songRepository.listAll().stream().map(s -> new SongDto(
                        s.getId(),
                        s.getTitle(),
                        s.getSpeed(),
                        s.getDances().stream().map(Dance::getId).toList()
                )
        ).toList();
    }

    @Transactional
    @POST
    public Response addSong(SongDto song) {
        songRepository.persist(new Song(
                song.id(),
                song.title(),
                song.speed(),
                song.danceIds().stream().map(id -> danceRepository.findById(id)).collect(Collectors.toSet())
        ));

        return Response.ok().build();
    }
}
