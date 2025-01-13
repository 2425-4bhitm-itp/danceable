package at.leonding.htl.features.library.dance;

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
}
