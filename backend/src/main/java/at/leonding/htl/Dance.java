package at.leonding.htl;

import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;

@Entity
public class Dance {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String name;
    private int minBPM;
    private int maxBPM;

    public void setId(Long id) {
        this.id = id;
    }

    public Long getId() {
        return id;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public int getMinBPM() {
        return minBPM;
    }

    public void setMinBPM(int minBPM) {
        this.minBPM = minBPM;
    }

    public int getMaxBPM() {
        return maxBPM;
    }

    public void setMaxBPM(int maxBPM) {
        this.maxBPM = maxBPM;
    }

    public Dance() {

    }
}
