package at.leonding.htl.features.library.songsnippet;

import at.leonding.htl.features.library.song.SongRepository;
import jakarta.inject.Inject;
import jakarta.transaction.Transactional;
import jakarta.ws.rs.*;
import jakarta.ws.rs.core.MediaType;
import jakarta.ws.rs.core.Response;

import java.util.List;

@Path("/snippets")
@Produces(MediaType.APPLICATION_JSON)
public class SongSnippetResource {
    @Inject
    SongSnippetRepository songSnippetRepository;

    @Inject
    SongRepository songRepository;

    @GET
    public List<SongSnippetDto> getAllSnippets() {
        return songSnippetRepository.listAll().stream()
                .map(s -> new SongSnippetDto(
                        s.getId(),
                        s.getSong().getId(),
                        s.getFileName())
                ).toList();
    }

    @Transactional
    @POST
    public Response addSnippet(SongSnippetDto snippet) {
        songSnippetRepository.persist(new SongSnippet(snippet.id(),
                songRepository.findById(snippet.id()),
                snippet.fileName()
        ));

        return Response.ok().build();
    }

    @Transactional
    @PATCH
    public Response patchSnippet(SongSnippetDto snippet) {
        SongSnippet songSnippet = songSnippetRepository.findById(snippet.id());

        songSnippet.setSong(songRepository.findById(snippet.id()));

        return Response.ok().build();
    }

    @Transactional
    @DELETE
    @Path("{id}")
    public Response deleteSnippet(@PathParam("id") Long id) {
        songSnippetRepository.deleteById(id);

        return Response.ok().build();
    }
}
