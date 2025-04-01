-- SQL to add user_id column to integrations table
ALTER TABLE integrations ADD COLUMN IF NOT EXISTS user_id INTEGER NOT NULL DEFAULT 1;
CREATE INDEX IF NOT EXISTS idx_integration_user_id ON integrations (user_id);
CREATE INDEX IF NOT EXISTS idx_integration_user_platform ON integrations (user_id, platform); 

-- Update any existing integrations to assign user_id=1 if they don't have a user_id
UPDATE integrations SET user_id = 1 WHERE user_id IS NULL;

-- Log that we've updated the table
INSERT INTO migration_log (description) VALUES ('Updated integrations table to ensure all records have user_id=1')
ON CONFLICT DO NOTHING; 