package at.leonding.htl.features.library.song;

import io.quarkus.hibernate.orm.panache.PanacheRepository;
import jakarta.enterprise.context.ApplicationScoped;

@ApplicationScoped
public class SongRepository implements PanacheRepository<Song> {
    public Song findSongByTitle(String title) {
        return find("title", title.toLowerCase()).firstResult();
    }

    public Song persistOrUpdateSong(String songName) {
        Song song = this.findSongByTitle(songName);

        if (song == null) {
            song = new Song(songName.toLowerCase());
            this.persist(song);
        }

        return song;
    }
}
