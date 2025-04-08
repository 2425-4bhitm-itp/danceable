package at.leonding.htl.features.library.clip;

import at.leonding.htl.features.library.song.Song;
import jakarta.persistence.*;
import jakarta.validation.constraints.NotEmpty;

import java.util.Objects;

@Entity
public class Clip {
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Id
    private Long id;

    @ManyToOne
    @JoinColumn(name = "song_id", nullable = false)
    private Song song;

    @NotEmpty
    private String fileName;

    public void setId(Long id) {
        this.id = id;
    }

    public Long getId() {
        return id;
    }

    public Song getSong() {
        return song;
    }

    public void setSong(Song song) {
        if (song == null) {
            throw new IllegalArgumentException("Song can not be null!");
        }

        this.song = song;
    }

    public String getFileName() {
        return fileName;
    }

    public void setFileName(String path) {
        this.fileName = path;
    }

    public Clip() {
    }

    public Clip(Song song) {
        this.song = song;
    }

    public Clip(Song song, String fileName) {
        this.song = song;
        this.fileName = fileName;
    }

    public Clip(Long id, Song song, String fileName) {
        this.id = id;
        this.song = song;
        this.fileName = fileName;
    }

    @Override
    public boolean equals(Object o) {
        if (o == null || getClass() != o.getClass()) return false;
        Clip that = (Clip) o;
        return Objects.equals(id, that.id);
    }

    @Override
    public int hashCode() {
        return Objects.hashCode(id);
    }

    @Override
    public String toString() {
        return "SongSnippet{" +
                "id=" + id +
                ", song=" + song +
                '}';
    }
}
