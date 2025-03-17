-- This file allow to write SQL commands that will be emitted in test and dev.
-- The commands are commented as their support depends of the database
-- insert into myentity (id, field) values(1, 'field-1');
-- insert into myentity (id, field) values(2, 'field-2');
-- insert into myentity (id, field) values(3, 'field-3');
-- alter sequence myentity_seq restart with 4;

INSERT INTO dance (name, minbpm, maxbpm)
VALUES
     ('Waltz', 84, 90),
     ('Vienese Waltz', 174, 180),
     ('Foxtrot', 112, 120),
     ('Quickstep', 200, 208),
     ('Tango', 120, 140),
     ('Cha Cha Cha', 120, 128),
     ('Rumba', 100, 108),
     ('Samba', 96, 104),
     ('Jive', 168, 184),
--      ('Paso Doble', 120, 124),
--      ('Lindy Hop', 105, 190),
--      ('Charleston', 200, 290),
--      ('Balboa', 175, 340),
--      ('East Coast Swing or Jitterbug', 120, 250),
     ('Blues Dance', 20, 75),
     ('Tango Argentino', 80, 160),
--      ('Tango Nuevo', 40, 160),
--      ('Milonga', 150, 240),
--      ('Vals', 150, 240),
     ('Salsa', 180, 300),
--      ('Merenge', 130, 200),
     ('Bachata', 90, 200);

INSERT INTO song (title) VALUES ('New Song Title');

-- Insert two song snippets for the new song
INSERT INTO SongSnippet (song_id, songSnippetIndex, speed, fileName)
VALUES
    ((SELECT id FROM song WHERE title = 'New Song Title'), 1, 120, 'snippet1.mp3'),
    ((SELECT id FROM song WHERE title = 'New Song Title'), 2, 130, 'snippet2.mp3');

select *
from song;
