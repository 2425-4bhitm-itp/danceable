package at.leonding.htl.features.prediction;

import io.quarkus.hibernate.orm.panache.PanacheRepository;
import jakarta.enterprise.context.ApplicationScoped;

@ApplicationScoped
public class PredictionRepository implements PanacheRepository<Prediction> {
}
