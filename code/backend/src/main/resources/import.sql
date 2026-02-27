-- Insert dances
 INSERT INTO Dance (name, minBpm, maxBpm, description)
 VALUES
     ('Slow Waltz', 84, 90, "A graceful ballroom dance in 3/4 time with smooth, flowing rise-and-fall movements and elegant progress around the floor."),
     ('Viennese Waltz', 174, 180, "A fast, rotating form of waltz in 3/4 time with continuous turns and sweeping movement around the floor; one of the oldest ballroom dances."),
     ('Quickstep', 200, 208, "A brisk, flowing ballroom dance evolved from foxtrot, featuring running steps, syncopations, and light hops; danced in a smooth style with continuous forward movement."),
     ('Tango', 200, 208, "A dramatic ballroom dance with sharp, staccato movements and purposeful pauses, expressing strong character and musical accents."),
     ('Cha Cha Cha', 120, 128, "A lively Latin partner dance with syncopated “cha-cha-cha” steps, playful hip motion, and rhythm that breaks on the 4th and 1st beats."),
     ('Rumba', 100, 108, "A slow, sensual Latin ballroom dance emphasizing hip action and romantic connection, with smooth, deliberate steps and steady rhythm."),
     ('Samba', 96, 104, "A rhythmic Latin dance from Brazil with a distinctive bounce action and forward-backward steps, often seen in both social and competitive dance scenes."),
     ('Jive', 168, 184, "A fast, energetic swing-influenced dance with quick rock-step and triple-step (shuffle) footwork, often danced to upbeat music in social and competitive settings."),
     ('Salsa', 180, 300, "A popular Latin partner dance with energetic footwork, rhythmically syncopated timing, spins, and dynamic lead-follow patterns; danced in clubs worldwide."),
     ('Discofox', 112, 120, "A versatile social partner dance from the disco era, combining simple forward-and-back or side steps with turns and wraps; danced to 4/4 music and easy to pick up by beginners."),

 -- Insert songs
-- INSERT INTO Song (title, speed, dance_id)
-- VALUES
--     ('Diamonds - Rihanna', 100, 1),
--     ('Bad Moon Rising - Creedence Clearwater Revival', 100, 2),
--     ('I Want It That Way - Backstreet Boys', 100, 1),
--     ('Havana - Camila Cabello', 100, 3),
--     ('All We Got - Ray Dalton', 100, 6),
--     ('Life is a Rollercoaster - Ronan Keating', 100, 5);
--
-- -- Insert clips
-- INSERT INTO Clip (song_id, fileName)
-- VALUES
--     (1, 'diamonds_rihanna_1.mp3'),
--     (2, 'bad_moon_rising_1.mp3'),
--     (2, 'bad_moon_rising_2.mp3'),
--     (2, 'bad_moon_rising_3.mp3'),
--     (3, 'i_want_it_that_way_1.mp3'),
--     (3, 'i_want_it_that_way_2.mp3'),
--     (3, 'i_want_it_that_way_3.mp3'),
--     (3, 'i_want_it_that_way_4.mp3'),
--     (4, 'havana_1.mp3'),
--     (4, 'havana_2.mp3'),
--     (4, 'havana_3.mp3'),
--     (5, 'all_we_got_1.mp3'),
--     (5, 'all_we_got_2.mp3'),
--     (6, 'life_is_a_rollercoaster_1.mp3'),
--     (6, 'life_is_a_rollercoaster_2.mp3');
--
-- -- Insert predictions
-- -- INSERT INTO Prediction (confidence, dance_id, speedCategory)
-- -- VALUES
-- --     (0.95, 1, 'slow'),
-- --     (0.85, 2, 'medium'),
-- --     (0.90, 3, 'fast');