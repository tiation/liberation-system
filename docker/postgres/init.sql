-- PostgreSQL initialization script for Liberation System
-- Creates database, user, and initial extensions

-- Create database (if running as superuser)
-- SELECT 'CREATE DATABASE liberation_system' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'liberation_system')\gexec

-- Connect to the liberation_system database
\c liberation_system;

-- Create extensions for enhanced functionality
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";
CREATE EXTENSION IF NOT EXISTS "btree_gist";

-- Create custom data types
CREATE TYPE transaction_status AS ENUM ('pending', 'processing', 'completed', 'failed', 'cancelled');
CREATE TYPE human_status AS ENUM ('active', 'inactive', 'suspended', 'pending');
CREATE TYPE distribution_type AS ENUM ('weekly_flow', 'housing_credit', 'investment_pool', 'emergency_fund', 'bonus');

-- Create liberation_user if not exists (for development)
DO
$do$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_roles
      WHERE rolname = 'liberation_user') THEN
      
      CREATE ROLE liberation_user LOGIN PASSWORD 'liberation_password';
   END IF;
END
$do$;

-- Grant necessary permissions
GRANT CONNECT ON DATABASE liberation_system TO liberation_user;
GRANT USAGE ON SCHEMA public TO liberation_user;
GRANT CREATE ON SCHEMA public TO liberation_user;

-- Create sequence for human IDs if needed
CREATE SEQUENCE IF NOT EXISTS human_id_seq START 1000000;

-- Create audit table for tracking changes
CREATE TABLE IF NOT EXISTS audit_log (
    id BIGSERIAL PRIMARY KEY,
    table_name TEXT NOT NULL,
    operation TEXT NOT NULL,
    old_values JSONB,
    new_values JSONB,
    user_id TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    session_id TEXT,
    ip_address INET
);

-- Create index on audit_log for performance
CREATE INDEX IF NOT EXISTS idx_audit_log_table_name ON audit_log(table_name);
CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp ON audit_log(timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_log_user_id ON audit_log(user_id);

-- Create function for audit logging
CREATE OR REPLACE FUNCTION audit_trigger_func()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        INSERT INTO audit_log (table_name, operation, old_values, timestamp)
        VALUES (TG_TABLE_NAME, TG_OP, to_jsonb(OLD), CURRENT_TIMESTAMP);
        RETURN OLD;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO audit_log (table_name, operation, old_values, new_values, timestamp)
        VALUES (TG_TABLE_NAME, TG_OP, to_jsonb(OLD), to_jsonb(NEW), CURRENT_TIMESTAMP);
        RETURN NEW;
    ELSIF TG_OP = 'INSERT' THEN
        INSERT INTO audit_log (table_name, operation, new_values, timestamp)
        VALUES (TG_TABLE_NAME, TG_OP, to_jsonb(NEW), CURRENT_TIMESTAMP);
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Create function for generating unique human IDs
CREATE OR REPLACE FUNCTION generate_human_id()
RETURNS TEXT AS $$
BEGIN
    RETURN 'H' || LPAD(nextval('human_id_seq')::TEXT, 9, '0');
END;
$$ LANGUAGE plpgsql;

-- Create function for calculating weekly distribution amounts
CREATE OR REPLACE FUNCTION calculate_weekly_distribution(
    base_amount DECIMAL(15,2) DEFAULT 800.00,
    adjustment_factor DECIMAL(5,2) DEFAULT 1.00,
    location_multiplier DECIMAL(5,2) DEFAULT 1.00
)
RETURNS DECIMAL(15,2) AS $$
BEGIN
    RETURN (base_amount * adjustment_factor * location_multiplier);
END;
$$ LANGUAGE plpgsql;

-- Create function for validating transaction amounts
CREATE OR REPLACE FUNCTION validate_transaction_amount(amount DECIMAL(15,2))
RETURNS BOOLEAN AS $$
BEGIN
    -- Basic validation: amount must be positive and reasonable
    RETURN amount > 0 AND amount <= 1000000;
END;
$$ LANGUAGE plpgsql;

-- Note: Materialized view will be created after tables are created by the application

-- Create function to refresh human stats
CREATE OR REPLACE FUNCTION refresh_human_stats()
RETURNS VOID AS $$
BEGIN
    REFRESH MATERIALIZED VIEW human_stats;
END;
$$ LANGUAGE plpgsql;

-- Create function for transaction statistics
CREATE OR REPLACE FUNCTION get_transaction_stats(
    start_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP - INTERVAL '30 days',
    end_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
)
RETURNS TABLE (
    transaction_type TEXT,
    count BIGINT,
    total_amount DECIMAL(15,2),
    avg_amount DECIMAL(15,2),
    min_amount DECIMAL(15,2),
    max_amount DECIMAL(15,2)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        t.transaction_type,
        COUNT(*)::BIGINT as count,
        SUM(t.amount) as total_amount,
        AVG(t.amount) as avg_amount,
        MIN(t.amount) as min_amount,
        MAX(t.amount) as max_amount
    FROM transactions t
    WHERE t.timestamp >= start_date AND t.timestamp <= end_date
    GROUP BY t.transaction_type
    ORDER BY total_amount DESC;
END;
$$ LANGUAGE plpgsql;

-- Create function for performance monitoring
CREATE OR REPLACE FUNCTION record_performance_metric(
    metric_name TEXT,
    metric_value DECIMAL(15,2),
    additional_metadata JSONB DEFAULT '{}'
)
RETURNS VOID AS $$
BEGIN
    INSERT INTO system_stats (metric_name, metric_value, metadata)
    VALUES (metric_name, metric_value, additional_metadata);
END;
$$ LANGUAGE plpgsql;

-- Grant permissions on all objects to liberation_user
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO liberation_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO liberation_user;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO liberation_user;

-- Note: Row level security and indexes will be created after tables are created by the application

-- Optimize PostgreSQL settings for the liberation system
ALTER SYSTEM SET shared_preload_libraries = 'pg_stat_statements';
ALTER SYSTEM SET track_activity_query_size = 2048;
ALTER SYSTEM SET log_min_duration_statement = 1000;
ALTER SYSTEM SET log_checkpoints = on;
ALTER SYSTEM SET log_connections = on;
ALTER SYSTEM SET log_disconnections = on;
ALTER SYSTEM SET log_lock_waits = on;

-- Create scheduled job to refresh statistics (if pg_cron is available)
-- SELECT cron.schedule('refresh-human-stats', '0 */6 * * *', 'SELECT refresh_human_stats()');

-- Note: Initial configuration and views will be created after tables are created by the application

-- Log successful initialization
INSERT INTO audit_log (table_name, operation, new_values)
VALUES ('system', 'INIT', '{"message": "Database initialized successfully", "timestamp": "' || CURRENT_TIMESTAMP || '"}');

-- Success message
SELECT 'Liberation System database initialized successfully!' as message;
