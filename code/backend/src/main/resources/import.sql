-- Insert dances
INSERT INTO dance (name, minbpm, maxbpm)
VALUES ('Waltz', 84, 90),
       ('Vienese Waltz', 174, 180),
       ('Foxtrott', 112, 120),
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

-- Insert songs
INSERT INTO song (title)
VALUES ('Diamonds - Rihanna'),
       ('Bad Moon Rising - Creedence Clearwater Revival'),
       ('I Want It That Way - Backstreet Boys'),
       ('Havana - Camila Cabello'),
       ('All We Got - Ray Dalton'),
       ('Life is a Rollercoaster - Ronan Keating');

-- Insert song snippets
INSERT INTO SongSnippet (song_id, songSnippetIndex, speed, fileName)
VALUES (1, 1, 85, 'diamonds_rihanna_1.mp3'),
       (2, 1, 44, 'bad_moon_rising_1.mp3'),
       (2, 2, 44, 'bad_moon_rising_2.mp3'),
       (2, 3, 44, 'bad_moon_rising_3.mp3'),
       (3, 1, 90, 'i_want_it_that_way_1.mp3'),
       (3, 2, 90, 'i_want_it_that_way_2.mp3'),
       (3, 3, 90, 'i_want_it_that_way_3.mp3'),
       (3, 4, 90, 'i_want_it_that_way_4.mp3'),
       (4, 1, 105, 'havana_1.mp3'),
       (4, 2, 105, 'havana_2.mp3'),
       (4, 3, 105, 'havana_3.mp3'),
       (5, 1, 116, 'all_we_got_1.mp3'),
       (5, 2, 116, 'all_we_got_2.mp3'),
       (6, 1, 120, 'life_is_a_rollercoaster_1.mp3'),
       (6, 2, 120, 'life_is_a_rollercoaster_2.mp3');

-- Link song snippets to dances
INSERT INTO songsnippet_dance (songsnippet_id, dances_id)
VALUES (1, 3),
       (2, 8),
       (2, 5),
       (3, 8),
       (3, 5),
       (4, 8),
       (4, 5),
       (5, 9),
       (5, 8),
       (5, 7),
       (6, 9),
       (6, 8),
       (6, 7),
       (7, 4),
       (7, 5),
       (7, 7),
       (8, 4),
       (8, 5),
       (8, 7),
       (9, 13),
       (9, 4),
       (10, 11),
       (10, 8),
       (11, 5),
       (12, 6),
       (12, 4);
