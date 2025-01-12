package at.leonding.htl.features.library.audiofile;

import at.leonding.htl.features.dance.Dance;
import at.leonding.htl.features.library.song.Song;
import jakarta.persistence.*;

import java.util.List;

@Entity
public class AudioFile {
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Id
    private Long id;

    @ManyToOne(optional = false)
    private Song song;

    @ManyToMany
    private List<Dance> dances;

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
}
