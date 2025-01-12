package at.leonding.htl.features.library.song;

import io.quarkus.hibernate.orm.panache.PanacheRepository;
import jakarta.enterprise.context.ApplicationScoped;

@ApplicationScoped
public class SongRepository implements PanacheRepository<Song> {
}
