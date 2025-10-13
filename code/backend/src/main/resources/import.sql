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
INSERT INTO Song (title, speed, dance_id)
VALUES
    ('Diamonds - Rihanna', 100, 1),
    ('Bad Moon Rising - Creedence Clearwater Revival', 100, 2),
    ('I Want It That Way - Backstreet Boys', 100, 1),
    ('Havana - Camila Cabello', 100, 3),
    ('All We Got - Ray Dalton', 100, 6),
    ('Life is a Rollercoaster - Ronan Keating', 100, 5);

-- Insert clips
INSERT INTO Clip (song_id, fileName)
VALUES
    (1, 'diamonds_rihanna_1.mp3'),
    (2, 'bad_moon_rising_1.mp3'),
    (2, 'bad_moon_rising_2.mp3'),
    (2, 'bad_moon_rising_3.mp3'),
    (3, 'i_want_it_that_way_1.mp3'),
    (3, 'i_want_it_that_way_2.mp3'),
    (3, 'i_want_it_that_way_3.mp3'),
    (3, 'i_want_it_that_way_4.mp3'),
    (4, 'havana_1.mp3'),
    (4, 'havana_2.mp3'),
    (4, 'havana_3.mp3'),
    (5, 'all_we_got_1.mp3'),
    (5, 'all_we_got_2.mp3'),
    (6, 'life_is_a_rollercoaster_1.mp3'),
    (6, 'life_is_a_rollercoaster_2.mp3');

-- Insert predictions
-- INSERT INTO Prediction (confidence, dance_id, speedCategory)
-- VALUES
--     (0.95, 1, 'slow'),
--     (0.85, 2, 'medium'),
--     (0.90, 3, 'fast');