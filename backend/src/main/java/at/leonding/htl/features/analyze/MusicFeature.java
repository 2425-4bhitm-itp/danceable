package at.leonding.htl.features.analyze;

import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "music_features")
public class MusicFeature {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    public Long id;

    @Column(name = "genre")
    public String genre;

    @Column(name = "feature_vector")
    @ElementCollection
    public double[] featureVector;

    @Column(name = "created_at")
    public LocalDateTime createdAt = LocalDateTime.now();

    // Getters and setters omitted for brevity
}
