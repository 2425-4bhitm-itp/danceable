package at.leonding.htl.features.dance;

import io.quarkus.hibernate.orm.panache.PanacheRepository;
import jakarta.enterprise.context.ApplicationScoped;

@ApplicationScoped
public class DanceRepository implements PanacheRepository<Dance> {
}
