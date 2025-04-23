package at.leonding.htl.features.library.song;

import at.leonding.htl.features.library.dance.Dance;
import at.leonding.htl.features.library.dance.DanceRepository;
import jakarta.inject.Inject;
import jakarta.transaction.Transactional;
import jakarta.ws.rs.*;
import jakarta.ws.rs.core.MediaType;
import jakarta.ws.rs.core.Response;

import java.net.URI;
import java.util.List;

@Path(SongResource.BASE_PATH)
@Produces(MediaType.APPLICATION_JSON)
public class SongResource {
    public static final String BASE_PATH = "/songs";

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
        Song song = new Song(
                songDto.title(),
                songDto.speed(),
                songDto.danceId() != null ? danceRepository.findById(songDto.danceId()) : null
        );

        songRepository.persist(song);

        return Response.created(URI.create(BASE_PATH + "/" + song.getId())).entity(song).build();
    }

    @Transactional
    @PATCH
    @Path("{id}")
    public Response patchSong1(String title, Integer speed, Long danceId) {
        try {
            if (title != null) {

            }

            if (speed != null) {

            }

            if (danceId != null) {

            }
        } catch (Exception e) {
            return Response.serverError().entity(e.getMessage()).build();
        }

        return Response.ok().build();
    }

    @Transactional
    @PATCH
    public Response patchSong(SongDto songDto) {
        try {
            Song song = songRepository.findById(songDto.id());
            Dance dance = danceRepository.findById(songDto.danceId());

            if (dance != null) {
                song.setDance(dance);
            }

            if (songDto.speed() != null) {
                song.setSpeed(songDto.speed());
            }
            if (songDto.title() != null) {
                song.setTitle(songDto.title());
            }
        } catch (Exception e) {
            return Response.serverError().entity(e.getMessage()).build();
        }

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
