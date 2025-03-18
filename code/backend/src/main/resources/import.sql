-- Insert dances (unchanged)
INSERT INTO dance (name, minbpm, maxbpm)
VALUES ('Waltz', 84, 90),
       ('Vienese Waltz', 174, 180),
       ('Foxtrot', 112, 120),
       ('Quickstep', 200, 208),
       ('Tango', 120, 140),
       ('Cha Cha Cha', 120, 128),
       ('Rumba', 100, 108),
       ('Samba', 96, 104),
       ('Jive', 168, 184),
       ('Blues Dance', 20, 75),
       ('Tango Argentino', 80, 160),
       ('Salsa', 180, 300),
       ('Bachata', 90, 200);

-- Example 1: Diamonds - Rihanna
INSERT INTO song (title)
VALUES ('Diamonds - Rihanna');

-- Insert song snippets for "Diamonds - Rihanna"
INSERT INTO SongSnippet (song_id, songSnippetIndex, speed, fileName)
VALUES (1, 1, 85, 'diamonds_rihanna_1.mp3');

-- Link snippets to dances
INSERT INTO songsnippet_dance (songsnippet_id, dances_id)
VALUES (1, 3);
-- Foxtrot

-- Example 2: Bad Moon Rising - Creedence Clearwater Revival
INSERT INTO song (title)
VALUES ('Bad Moon Rising - Creedence Clearwater Revival');

-- Insert song snippets for "Bad Moon Rising"
INSERT INTO SongSnippet (song_id, songSnippetIndex, speed, fileName)
VALUES (2, 1, 44, 'bad_moon_rising_1.mp3'),
       (2, 2, 44, 'bad_moon_rising_2.mp3'),
       (2, 3, 44, 'bad_moon_rising_3.mp3');

-- Link snippets to dances
INSERT INTO songsnippet_dance (songsnippet_id, dances_id)
VALUES (1, 8), -- Disco Fox
       (1, 5), -- Tango
       (2, 8), -- Disco Fox
       (2, 5), -- Tango
       (3, 8), -- Disco Fox
       (3, 5);
-- Tango

-- Example 3: I Want It That Way - Backstreet Boys
INSERT INTO song (title)
VALUES ('I Want It That Way - Backstreet Boys');

-- Insert song snippets for "I Want It That Way"
INSERT INTO SongSnippet (song_id, songSnippetIndex, speed, fileName)
VALUES (3, 1, 90, 'i_want_it_that_way_1.mp3'),
       (3, 2, 90, 'i_want_it_that_way_2.mp3'),
       (3, 3, 90, 'i_want_it_that_way_3.mp3'),
       (3, 4, 90, 'i_want_it_that_way_4.mp3');

-- Link snippets to dances
INSERT INTO songsnippet_dance (songsnippet_id, dances_id)
VALUES (1, 9), -- Jive
       (1, 8), -- Disco Fox
       (1, 7), -- Samba
       (2, 9), -- Jive
       (2, 8), -- Disco Fox
       (2, 7), -- Samba
       (3, 9), -- Jive
       (3, 8), -- Disco Fox
       (3, 7), -- Samba
       (4, 9), -- Jive
       (4, 8), -- Disco Fox
       (4, 7);
-- Samba

-- Example 4: Havana - Camila Cabello
INSERT INTO song (title)
VALUES ('Havana - Camila Cabello');

-- Insert song snippets for "Havana - Camila Cabello"
INSERT INTO SongSnippet (song_id, songSnippetIndex, speed, fileName)
VALUES (4, 1, 105, 'havana_1.mp3'),
       (4, 2, 105, 'havana_2.mp3'),
       (4, 3, 105, 'havana_3.mp3');

-- Link snippets to dances
INSERT INTO songsnippet_dance (songsnippet_id, dances_id)
VALUES (1, 4),
       (2, 4),
       (3, 4);
-- Quickstep

-- Example 5: All We Got - Ray Dalton
INSERT INTO song (title)
VALUES ('All We Got - Ray Dalton');

-- Insert song snippets for "All We Got"
INSERT INTO SongSnippet (song_id, songSnippetIndex, speed, fileName)
VALUES (5, 1, 116, 'all_we_got_1.mp3'),
       (5, 2, 116, 'all_we_got_2.mp3');

-- Link snippets to dances
INSERT INTO songsnippet_dance (songsnippet_id, dances_id)
VALUES (1, 9), -- Jive
       (1, 8), -- Disco Fox
       (2, 9), -- Jive
       (2, 8);
-- Disco Fox

-- Example 6: Life is a Rollercoaster - Ronan Keating
INSERT INTO song (title)
VALUES ('Life is a Rollercoaster - Ronan Keating');

-- Insert song snippets for "Life is a Rollercoaster"
INSERT INTO SongSnippet (song_id, songSnippetIndex, speed, fileName)
VALUES (6, 1, 120, 'life_is_a_rollercoaster_1.mp3'),
       (6, 2, 120, 'life_is_a_rollercoaster_2.mp3');

-- Link snippets to dances
INSERT INTO songsnippet_dance (songsnippet_id, dances_id)
VALUES (1, 3), -- Slow Fox
       (2, 3); -- Slow Fox
