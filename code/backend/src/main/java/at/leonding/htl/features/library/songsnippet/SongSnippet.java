package at.leonding.htl.features.library.songsnippet;

import at.leonding.htl.features.library.song.Song;
import jakarta.persistence.*;

import java.util.Objects;

@Entity
public class SongSnippet {
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Id
    private Long id;

    @ManyToOne
    @JoinColumn(name = "song_id", nullable = false)
    private Song song;

    private int songSnippetIndex = 0;

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

    public int getSongSnippetIndex() {
        return songSnippetIndex;
    }

    public void setSongSnippetIndex(int songSnippetIndex) {
        this.songSnippetIndex = songSnippetIndex;
    }

    public String getFileName() {
        return fileName;
    }

    public void setFileName(String path) {
        this.fileName = path;
    }

    public SongSnippet() {
    }

    public SongSnippet(Song song) {
        this.song = song;
    }

    public SongSnippet(Song song, int songSnippetIndex, String fileName) {
        this.song = song;
        this.songSnippetIndex = songSnippetIndex;
        this.fileName = fileName;
    }

    public SongSnippet(Long id, Song song, int songSnippetIndex, String fileName) {
        this.id = id;
        this.song = song;
        this.songSnippetIndex = songSnippetIndex;
        this.fileName = fileName;
    }

    @Override
    public boolean equals(Object o) {
        if (o == null || getClass() != o.getClass()) return false;
        SongSnippet that = (SongSnippet) o;
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
                ", songSnippetIndex=" + songSnippetIndex +
                '}';
    }
}
