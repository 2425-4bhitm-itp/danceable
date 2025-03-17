package at.leonding.htl.features.library.song;

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

    @GET
    public List<Song> getAllSongs() {
        return songRepository.listAll();
    }

    @Transactional
    @POST
    public Response addSong(Song song) {
        songRepository.persist(song);
        return Response.ok().build();
    }
}
