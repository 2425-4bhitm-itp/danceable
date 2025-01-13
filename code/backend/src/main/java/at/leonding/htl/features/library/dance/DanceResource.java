package at.leonding.htl.features.library.dance;

import jakarta.inject.Inject;
import jakarta.ws.rs.GET;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.QueryParam;
import jakarta.ws.rs.core.MediaType;

import java.util.List;

@Path("/dances")
@Produces(MediaType.APPLICATION_JSON)
public class DanceResource {
    @Inject
    DanceRepository danceRepository;

    @GET
    public List<Dance> getAllDances() {
        return danceRepository.listAll();
    }

    @Path("/speed")
    @GET
    public List<Dance> getDanceInBpmRange(@QueryParam("bpm") int bpm) {
        return danceRepository.find("minBpm <= ?1 and maxBpm >= ?2", bpm, bpm).list();
    }
}
