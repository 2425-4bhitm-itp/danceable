package at.leonding.htl.features.library.songsnippet;

import at.leonding.htl.features.library.dance.Dance;
import at.leonding.htl.features.library.song.Song;
import jakarta.persistence.*;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotEmpty;

import java.util.Objects;
import java.util.Set;

@Entity
public class SongSnippet {
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Id
    private Long id;

    @ManyToOne
    @JoinColumn(name = "song_id", nullable = false)
    private Song song;

    @ManyToMany(cascade = CascadeType.MERGE)
    private Set<Dance> dances;

    private int songSnippetIndex = 0;

    @Min(0)
    private int speed;

//    @NotEmpty
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
        this.song = song;
    }

    public Set<Dance> getDances() {
        return dances;
    }

    public void setDances(Set<Dance> dances) {
        this.dances = dances;
    }

    public int getSongSnippetIndex() {
        return songSnippetIndex;
    }

    public void setSongSnippetIndex(int songSnippetIndex) {
        this.songSnippetIndex = songSnippetIndex;
    }

    public void addDance(Dance dance) {
        this.dances.add(dance);
    }

    public boolean removeDance(Dance dance) {
        return this.dances.remove(dance);
    }

    public String getFileName() {
        return fileName;
    }

    public void setFileName(String path) {
        this.fileName = path;
    }

    public int getSpeed() {
        return speed;
    }

    public void setSpeed(int speed) {
        this.speed = speed;
    }

    public SongSnippet() {
    }

    public SongSnippet(Song song) {
        this.song = song;
    }

    public SongSnippet(Song song, int songSnippetIndex) {
        this.song = song;
        this.songSnippetIndex = songSnippetIndex;
    }

    public SongSnippet(Song song, int songSnippetIndex, Set<Dance> dances) {
        this.songSnippetIndex = songSnippetIndex;
        this.dances = dances;
        this.song = song;
    }

    public SongSnippet(Song song, Set<Dance> dances, int songSnippetIndex, int speed, String fileName) {
        this.song = song;
        this.dances = dances;
        this.songSnippetIndex = songSnippetIndex;
        this.speed = speed;
        this.fileName = fileName;
    }

    @Override
    public boolean equals(Object o) {
        if (o == null || getClass() != o.getClass()) return false;
        SongSnippet songSnippet = (SongSnippet) o;
        return Objects.equals(id, songSnippet.id);
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
                ", dances=" + dances +
                ", songSnippetIndex=" + songSnippetIndex +
                '}';
    }
}
