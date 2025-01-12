package at.leonding.htl.features.library.audiofile;

import io.quarkus.hibernate.orm.panache.PanacheRepository;
import jakarta.enterprise.context.ApplicationScoped;

@ApplicationScoped
public class AudioFileRepository implements PanacheRepository<AudioFile> {
}
