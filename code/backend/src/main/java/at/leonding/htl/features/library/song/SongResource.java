package at.leonding.htl.features.library.song;

import at.leonding.htl.features.library.dance.DanceRepository;
import jakarta.inject.Inject;
import jakarta.transaction.Transactional;
import jakarta.ws.rs.*;
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

    @Transactional
    @PATCH
    public Response patchSong(SongDto songDto) {
        Song song = songRepository.findById(songDto.id());

        song.setDance(danceRepository.findById(songDto.danceId()));
        song.setSpeed(songDto.speed());
        song.setTitle(songDto.title());

        return Response.ok().build();
    }

    @Transactional
    @DELETE
    @Path("{id}")
    public Response deleteSong(@PathParam("id") Long id) {
        songRepository.deleteById(id);

        return Response.ok().build();
    }
}
