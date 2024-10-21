package at.leonding.htl.features.analyze.fourier;

import io.quarkus.hibernate.orm.panache.PanacheRepository;
import jakarta.enterprise.context.ApplicationScoped;

@ApplicationScoped
public class MusicFeatureRepository implements PanacheRepository<MusicFeature> {

}
