package at.leonding.htl.features.prediction;

import at.leonding.htl.features.library.dance.Dance;
import jakarta.persistence.*;
import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;

import java.util.Objects;

@Entity
public class Prediction {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne
    @JoinColumn(name = "dance_id")
    private Dance dance;

    @Min(value = 0)
    @Max(value = 1)
    private double confidence;

    @Enumerated(value = EnumType.STRING)
    private SpeedCategory speedCategory;

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public Dance getDance() {
        return dance;
    }

    public void setDance(Dance dance) {
        this.dance = dance;
    }

    public double getConfidence() {
        return confidence;
    }

    public void setConfidence(double confidence) {
        this.confidence = confidence;
    }

    public SpeedCategory getSpeedCategory() {
        return speedCategory;
    }

    public void setSpeedCategory(SpeedCategory speedCategory) {
        this.speedCategory = speedCategory;
    }

    public Prediction() {
    }

    @Override
    public boolean equals(Object o) {
        if (o == null || getClass() != o.getClass()) return false;
        Prediction that = (Prediction) o;
        return Objects.equals(id, that.id);
    }

    @Override
    public int hashCode() {
        return Objects.hashCode(id);
    }
}