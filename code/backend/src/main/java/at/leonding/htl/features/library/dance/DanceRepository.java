package at.leonding.htl.features.library.dance;

import io.quarkus.hibernate.orm.panache.PanacheRepository;
import jakarta.enterprise.context.ApplicationScoped;

@ApplicationScoped
public class DanceRepository implements PanacheRepository<Dance> {
    public Dance findDanceByName(String name) {
        return find("name", name).stream().findFirst().orElse(null);
    }

    public Dance persistOrUpdateSong(String danceName) {
        Dance dance = this.findDanceByName(danceName);

        if (dance == null) {
            dance = new Dance(danceName);
            this.persist(dance);
        }

        return dance;
    }
}