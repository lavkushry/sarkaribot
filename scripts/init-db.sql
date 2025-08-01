-- Initialize SarkariBot Database
-- This script runs when PostgreSQL container starts

-- Create additional schemas if needed
CREATE SCHEMA IF NOT EXISTS analytics;
CREATE SCHEMA IF NOT EXISTS monitoring;
CREATE SCHEMA IF NOT EXISTS alerts;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create indexes for better performance
-- (Django will create tables, but we can prepare some optimizations)

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE sarkaribot_dev TO sarkaribot_user;
GRANT ALL PRIVILEGES ON DATABASE sarkaribot_preprod TO sarkaribot_user;

-- Set timezone
SET timezone = 'UTC';

-- Log initialization
INSERT INTO pg_stat_statements_info (dealloc) VALUES (0) ON CONFLICT DO NOTHING;
