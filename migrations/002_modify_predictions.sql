-- migrate:up
ALTER TABLE predictions
ADD COLUMN IF NOT EXISTS employment_type VARCHAR(255) NOT NULL DEFAULT 'fulltime',
ADD COLUMN IF NOT EXISTS result JSON DEFAULT '{}';

-- migrate:down
ALTER TABLE predictions 
DROP COLUMN IF EXISTS employment_type,
DROP COLUMN IF EXISTS result;