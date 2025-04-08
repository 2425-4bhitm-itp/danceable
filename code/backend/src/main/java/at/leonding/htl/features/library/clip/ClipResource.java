package at.leonding.htl.features.library.clip;

import at.leonding.htl.features.library.song.SongRepository;
import jakarta.inject.Inject;
import jakarta.transaction.Transactional;
import jakarta.ws.rs.*;
import jakarta.ws.rs.core.MediaType;
import jakarta.ws.rs.core.Response;

import java.net.URI;
import java.util.List;

@Path(ClipResource.BASE_PATH)
@Produces(MediaType.APPLICATION_JSON)
public class ClipResource {
    public static final String BASE_PATH = "/clips";

    @Inject
    ClipRepository clipRepository;

    @Inject
    SongRepository songRepository;

    @GET
    public List<ClipDto> getAllClips() {
        return clipRepository.listAll().stream()
                .map(s -> new ClipDto(
                        s.getId(),
                        s.getSong().getId(),
                        s.getFileName())
                ).toList();
    }

    @Transactional
    @POST
    public Response addClip(ClipDto clipDto) {
        Clip clip = new Clip(clipDto.id(),
                songRepository.findById(clipDto.id()),
                clipDto.fileName()
        );

        clipRepository.persist(clip);

        return Response.created(URI.create(BASE_PATH + "/" + clip.getId())).build();
    }

    @Transactional
    @PATCH
    public Response patchClip(ClipDto clipDto) {
        try {
            Clip clip = clipRepository.findById(clipDto.id());

            if (clip != null && clipDto.songId() > 0) {
                clip.setSong(songRepository.findById(clipDto.songId()));
            }
        } catch (Exception e) {
            return Response.serverError().entity(e.getMessage()).build();
        }

        return Response.ok().build();
    }

    @Transactional
    @DELETE
    @Path("{id}")
    public Response deleteClip(@PathParam("id") Long id) {
        clipRepository.deleteById(id);

        return Response.ok().build();
    }
}
