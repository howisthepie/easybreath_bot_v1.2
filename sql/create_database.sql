CREATE TABLE IF NOT EXISTS messages (
  user_id INTEGER,
  role TEXT,
  content TEXT
)
CREATE INDEX IF NOT EXISTS messages_id_idx ON messages(user_id);
