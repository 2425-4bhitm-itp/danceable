package at.leonding.htl.features.library.songsnippet;

import at.leonding.htl.features.library.dance.Dance;
import at.leonding.htl.features.library.song.Song;
import io.quarkus.hibernate.orm.panache.PanacheRepository;
import jakarta.enterprise.context.ApplicationScoped;

import java.util.Set;

@ApplicationScoped
public class SongSnippetRepository implements PanacheRepository<SongSnippet> {
    public SongSnippet findSongSnippetBySongAndIndex(Song song, int index) {
        return find("song = ?1 and songSnippetIndex = ?2", song, index).list().stream()
                .findFirst()
                .orElse(null);
    }

    public SongSnippet persistOrUpdateSongSnippet(Song song, int songSnippetIndex, int speedInBpm, Set<Dance> dances, String path) {
        SongSnippet songSnippet = this.findSongSnippetBySongAndIndex(song, songSnippetIndex);

        if (songSnippet == null) {
            songSnippet = new SongSnippet(song, dances, songSnippetIndex, speedInBpm, path);
        } else {
            songSnippet.setSpeed(speedInBpm);
            songSnippet.setDances(dances);
            songSnippet.setFileName(path);
        }

        this.persist(songSnippet);

        return songSnippet;
    }
}