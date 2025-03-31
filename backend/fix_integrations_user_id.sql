-- SQL to add user_id column to integrations table
ALTER TABLE integrations ADD COLUMN IF NOT EXISTS user_id INTEGER NOT NULL DEFAULT 1;
CREATE INDEX IF NOT EXISTS idx_integration_user_id ON integrations (user_id);
CREATE INDEX IF NOT EXISTS idx_integration_user_platform ON integrations (user_id, platform); 