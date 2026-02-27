package at.leonding.htl.features.library.dance;

import jakarta.persistence.*;

import java.util.Objects;

@Entity
public class Dance implements Comparable<Dance> {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(unique=true)
    private String name;
    private int minBpm;
    private int maxBpm;
    private String description;
    private String androidImageLink;
    private String androidImageLinkLady;

    public String getAndroidImageLinkLady() {
        return androidImageLinkLady;
    }

    public void setAndroidImageLinkLady(String androidImageLinkLady) {
        this.androidImageLinkLady = androidImageLinkLady;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public String getAndroidImageLink() {
        return androidImageLink;
    }

    public void setAndroidImageLink(String androidImageLink) {
        this.androidImageLink = androidImageLink;
    }

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

    public Dance(String name, int minBpm, int maxBpm) {
        this.name = name;
        this.minBpm = minBpm;
        this.maxBpm = maxBpm;
    }

    public Dance(String name, int minBpm, int maxBpm, String description) {
        this.name = name;
        this.minBpm = minBpm;
        this.maxBpm = maxBpm;
        this.description = description;
    }

    public Dance(String name, int minBpm, int maxBpm, String description, String androidImageLink) {
        this.name = name;
        this.minBpm = minBpm;
        this.maxBpm = maxBpm;
        this.description = description;
        this.androidImageLink = androidImageLink;
    }

    public Dance(String name, int minBpm, int maxBpm, String description, String androidImageLink, String androidImageLinkLady) {
        this.name = name;
        this.minBpm = minBpm;
        this.maxBpm = maxBpm;
        this.description = description;
        this.androidImageLink = androidImageLink;
        this.androidImageLinkLady = androidImageLinkLady;
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
