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

    @ManyToOne(cascade = CascadeType.MERGE)
    @JoinColumn(name = "dance_id")
    private Dance dance;

    private int speed;

    public int getSpeed() {
        return speed;
    }

    public void setSpeed(int speed) {
        this.speed = speed;
    }

    public Dance getDance() {
        return dance;
    }

    public void setDance(Dance dance) {
        this.dance = dance;
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

    public Song(String title, int speed, Dance dance) {
        this(title, speed);
        this.dance = dance;
    }

    public Song(Long id, String title, int speed, Dance dance) {
        this(title, speed, dance);
        this.id = id;
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
