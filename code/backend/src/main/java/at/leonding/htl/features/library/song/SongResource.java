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
                        s.getDance().getId()
                )
        ).toList();
    }

    @Transactional
    @POST
    public Response addSong(SongDto songDto) {
        songRepository.persist(new Song(
                songDto.id(),
                songDto.title(),
                songDto.speed(),
                danceRepository.findById(songDto.danceId())
        ));

        return Response.ok().build();
    }
}
