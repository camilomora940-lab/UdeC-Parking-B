-- 1. Create the sectors table
CREATE TABLE sectors (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  short_name TEXT NOT NULL,
  emoji TEXT,
  lat FLOAT NOT NULL,
  lng FLOAT NOT NULL,
  capacity INTEGER NOT NULL,
  occupied INTEGER NOT NULL DEFAULT 0,
  zone TEXT,
  level TEXT,
  hours TEXT,
  contact TEXT
);

-- 2. Insert initial data
INSERT INTO sectors (id, name, short_name, emoji, lat, lng, capacity, occupied, zone, level, hours, contact) VALUES
('ing', 'Facultad de Ingeniería', 'Ingeniería', '🏗️', -36.83024257931655, -73.03716784417536, 120, 45, 'Norte', 'surface', 'Lun–Vie 7:00–21:00', '+56 41 2204557'),
('bib', 'Biblioteca Central', 'Biblioteca', '📚', -36.83268227916819, -73.03497202829713, 80, 20, 'Centro', 'surface', 'Lun–Vie 7:30–22:00', '+56 41 2204558');

-- 3. Enable Row Level Security (RLS)
ALTER TABLE sectors ENABLE ROW LEVEL SECURITY;

-- 4. Create policies so anyone can read the sectors data
CREATE POLICY "Public profiles are viewable by everyone."
  ON sectors FOR SELECT
  USING ( true );

-- 5. Enable Realtime for the sectors table
alter publication supabase_realtime add table sectors;

-- 6. Create RPC for incrementing and decrementing occupied spaces
CREATE OR REPLACE FUNCTION increment_occupied(sector_id text)
RETURNS void
LANGUAGE sql
AS $$
  UPDATE sectors
  SET occupied = occupied + 1
  WHERE id = sector_id AND occupied < capacity;
$$;

CREATE OR REPLACE FUNCTION decrement_occupied(sector_id text)
RETURNS void
LANGUAGE sql
AS $$
  UPDATE sectors
  SET occupied = occupied - 1
  WHERE id = sector_id AND occupied > 0;
$$;
