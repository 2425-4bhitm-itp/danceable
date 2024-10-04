package at.leonding.htl.features.analyze;

import io.quarkus.hibernate.orm.panache.PanacheRepository;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.transaction.Transactional;
import java.util.List;

@ApplicationScoped
public class VectorRepository implements PanacheRepository<VectorEntity> {

    @Transactional
    public void saveVector(double[] vector, String category) {
        VectorEntity entity = new VectorEntity();
        entity.vector = vector;
        entity.category = category;
        persist(entity);
    }

    public List<VectorEntity> findByCategory(String category) {
        return list("category", category);
    }
}
