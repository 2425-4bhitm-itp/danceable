package at.leonding.htl.features.library.songsnippet;

public record SongSnippetDto(
        Long id,
        Long songId,
        int songSnippetIndex,
        String fileName
) {
}
