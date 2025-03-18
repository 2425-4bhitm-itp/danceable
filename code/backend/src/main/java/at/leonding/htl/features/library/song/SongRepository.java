package at.leonding.htl.features.library.song;

import at.leonding.htl.features.library.dance.Dance;
import io.quarkus.hibernate.orm.panache.PanacheRepository;
import jakarta.enterprise.context.ApplicationScoped;

import java.util.Set;

@ApplicationScoped
public class SongRepository implements PanacheRepository<Song> {
    public Song findSongByTitle(String title) {
        return find("title", title.toLowerCase()).firstResult();
    }

    public Song persistOrUpdateSong(String songName, Set<Dance> dances) {
        Song song = this.findSongByTitle(songName);

        if (song == null) {
            song = new Song(songName.toLowerCase(), dances);
        } else {
            song.setDances(dances);
        }

        this.persist(song);

        return song;
    }
}
