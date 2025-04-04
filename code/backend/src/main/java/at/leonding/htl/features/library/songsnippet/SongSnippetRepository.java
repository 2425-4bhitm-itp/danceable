package at.leonding.htl.features.library.songsnippet;

import at.leonding.htl.features.library.song.Song;
import io.quarkus.hibernate.orm.panache.PanacheRepository;
import jakarta.enterprise.context.ApplicationScoped;

@ApplicationScoped
public class SongSnippetRepository implements PanacheRepository<SongSnippet> {
    public SongSnippet findSongSnippetBySongAndIndex(Song song, int index) {
        return find("song = ?1 and songSnippetIndex = ?2", song, index).firstResult();
    }

    public SongSnippet persistOrUpdateSongSnippet(Song song, String path) {
//        SongSnippet songSnippet = this.findSongSnippetBySongAndIndex(song, songSnippetIndex); // warummm?????
        SongSnippet songSnippet = null;

        if (songSnippet == null) {
            songSnippet = new SongSnippet(song, path);
        } else {
            songSnippet.setFileName(path);
        }

        this.persist(songSnippet);

        return songSnippet;
    }
}