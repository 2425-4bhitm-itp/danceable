package at.leonding.htl.features.library.song;

import java.util.List;

public record SongDto(
        Long id,
        String title,
        int speed,
        List<Long> danceIds
) {
}
