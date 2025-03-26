package at.leonding.htl.features.library.song;

import at.leonding.htl.features.library.dance.Dance;
import jakarta.persistence.*;
import jakarta.validation.constraints.Min;

import java.util.Objects;
import java.util.Set;
import java.util.SortedSet;
import java.util.TreeSet;

@Entity
public class Song {
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Id
    private Long id;

    @Column(unique = true)
    private String title;

    @ManyToMany(cascade = CascadeType.MERGE)
    private SortedSet<Dance> dances;

    private int speed;

    public int getSpeed() {
        return speed;
    }

    public void setSpeed(int speed) {
        this.speed = speed;
    }

    public Set<Dance> getDances() {
        return dances;
    }

    public void setDances(Set<Dance> dances) {
        this.dances = new TreeSet<>(dances);
    }

    public void setDances(SortedSet<Dance> dances) {
        this.dances = dances;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public Long getId() {
        return id;
    }

    public String getTitle() {
        return title;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public Song() {
    }

    public Song(String title) {
        this.title = title;
    }

    public Song(String title, int speed) {
        this(title);
        this.speed = speed;
    }

    public Song(String title, int speed, Set<Dance> dances) {
        this(title, speed, new TreeSet<>(dances));
    }

    public Song(String title, int speed, SortedSet<Dance> dances) {
        this(title, speed);
        this.dances = dances;
    }

    public Song(Long id, String title, int speed, SortedSet<Dance> dances) {
        this(title, speed, dances);
        this.id = id;
    }

    public Song(Long id, String title, int speed, Set<Dance> dances) {
        this(title, speed, dances);
        this.id = id;
    }

    public void addDance(Dance dance) {
        this.dances.add(dance);
    }

    public boolean removeDance(Dance dance) {
        return this.dances.remove(dance);
    }

    @Override
    public boolean equals(Object o) {
        if (o == null || getClass() != o.getClass()) return false;
        Song song = (Song) o;
        return Objects.equals(id, song.id);
    }

    @Override
    public int hashCode() {
        return Objects.hashCode(id);
    }

    @Override
    public String toString() {
        return "Song{" +
                "id=" + id +
                ", title='" + title + '\'' +
                '}';
    }
}
