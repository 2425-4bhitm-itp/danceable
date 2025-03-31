-- Insert dances
INSERT INTO Dance (name, minBpm, maxBpm) 
VALUES 
    ('Slow Waltz', 84, 90),
    ('Viennese Waltz', 174, 180),
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
INSERT INTO Song (title, speed)
VALUES 
    ('Diamonds - Rihanna', 100),
    ('Bad Moon Rising - Creedence Clearwater Revival', 100),
    ('I Want It That Way - Backstreet Boys', 100),
    ('Havana - Camila Cabello', 100),
    ('All We Got - Ray Dalton', 100),
    ('Life is a Rollercoaster - Ronan Keating', 100);

-- Insert song snippets
INSERT INTO SongSnippet (song_id, songSnippetIndex, fileName)
VALUES
    (1, 1, 'diamonds_rihanna_1.mp3'),
    (2, 1, 'bad_moon_rising_1.mp3'),
    (2, 2, 'bad_moon_rising_2.mp3'),
    (2, 3, 'bad_moon_rising_3.mp3'),
    (3, 1, 'i_want_it_that_way_1.mp3'),
    (3, 2, 'i_want_it_that_way_2.mp3'),
    (3, 3, 'i_want_it_that_way_3.mp3'),
    (3, 4, 'i_want_it_that_way_4.mp3'),
    (4, 1, 'havana_1.mp3'),
    (4, 2, 'havana_2.mp3'),
    (4, 3, 'havana_3.mp3'),
    (5, 1, 'all_we_got_1.mp3'),
    (5, 2, 'all_we_got_2.mp3'),
    (6, 1, 'life_is_a_rollercoaster_1.mp3'),
    (6, 2, 'life_is_a_rollercoaster_2.mp3');

-- Link songs to dances
INSERT INTO Song_Dance (Song_id, dances_id)
VALUES
    (1, 3),
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
    (6, 7);

-- Insert predictions
INSERT INTO Prediction (confidence, dance_id, speedCategory)
VALUES
    (0.95, 1, 'slow'),
    (0.85, 2, 'medium'),
    (0.90, 3, 'fast');