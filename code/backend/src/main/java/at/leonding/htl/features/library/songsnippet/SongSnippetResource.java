package at.leonding.htl.features.library.songsnippet;

import jakarta.inject.Inject;
import jakarta.transaction.Transactional;
import jakarta.ws.rs.GET;
import jakarta.ws.rs.POST;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.core.MediaType;
import jakarta.ws.rs.core.Response;

import java.util.List;

@Path("/snippets")
@Produces(MediaType.APPLICATION_JSON)
public class SongSnippetResource {
    @Inject
    SongSnippetRepository songSnippetRepository;

    @GET
    public List<SongSnippet> getAllSnippets() {
        return songSnippetRepository.listAll();
    }

    @Transactional
    @POST
    public Response addSnippet(SongSnippet snippet) {
        songSnippetRepository.persist(snippet);
        return Response.ok().build();
    }
}
