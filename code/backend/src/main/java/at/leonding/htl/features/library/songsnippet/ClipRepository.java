package at.leonding.htl.features.library.songsnippet;

import at.leonding.htl.features.library.song.Song;
import io.quarkus.hibernate.orm.panache.PanacheRepository;
import jakarta.enterprise.context.ApplicationScoped;

@ApplicationScoped
public class ClipRepository implements PanacheRepository<Clip> {
    public Clip findSongSnippetBySongAndIndex(Song song, int index) {
        return find("song = ?1 and songSnippetIndex = ?2", song, index).firstResult();
    }

    public Clip persistOrUpdateSongSnippet(Song song, String path) {
//        SongSnippet songSnippet = this.findSongSnippetBySongAndIndex(song, songSnippetIndex); // warummm?????
        Clip clip = null;

        if (clip == null) {
            clip = new Clip(song, path);
        } else {
            clip.setFileName(path);
        }

        this.persist(clip);

        return clip;
    }
}