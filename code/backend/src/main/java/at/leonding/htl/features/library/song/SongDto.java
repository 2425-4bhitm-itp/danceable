package at.leonding.htl.features.library.song;

public record SongDto(
        Long id,
        String title,
        Integer speed,
        Long danceId
) {
}
