package at.leonding.htl.features.library.dance;

import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;

import java.util.Objects;

@Entity
public class Dance implements Comparable<Dance> {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String name;
    private int minBpm;
    private int maxBpm;

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

    public int getMinBpm() {
        return minBpm;
    }

    public void setMinBpm(int minBpm) {
        this.minBpm = minBpm;
    }

    public int getMaxBpm() {
        return maxBpm;
    }

    public void setMaxBpm(int maxBpm) {
        this.maxBpm = maxBpm;
    }

    public boolean isBpmInRange(double bpmToCheck){
        boolean originalBpmIsInRange = bpmToCheck >= minBpm && bpmToCheck <= maxBpm;
        if(!originalBpmIsInRange){
            if(bpmToCheck * 2 >= minBpm && bpmToCheck * 2 <= maxBpm ||
                bpmToCheck / 2 >= minBpm && bpmToCheck / 2 <= maxBpm){
                return true;
            }
        }
        return originalBpmIsInRange;
    }

    public Dance() {
    }

    public Dance(String name) {
        this.name = name;
    }

    @Override
    public boolean equals(Object o) {
        if (o == null || getClass() != o.getClass()) return false;
        Dance dance = (Dance) o;
        return Objects.equals(id, dance.id);
    }

    @Override
    public int hashCode() {
        return Objects.hashCode(id);
    }

    @Override
    public int compareTo(Dance o) {
        return this.name.compareTo(o.name) * (-1);
    }
}
