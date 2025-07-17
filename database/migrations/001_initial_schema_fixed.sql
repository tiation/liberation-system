-- Liberation System Database Schema
-- PostgreSQL Migration Script

-- Database should be created separately with createdb
-- We're already connected to liberation_system database

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Create schemas
CREATE SCHEMA IF NOT EXISTS core;
CREATE SCHEMA IF NOT EXISTS resources;
CREATE SCHEMA IF NOT EXISTS truth;
CREATE SCHEMA IF NOT EXISTS mesh;
CREATE SCHEMA IF NOT EXISTS analytics;

-- Core system tables
CREATE TABLE IF NOT EXISTS core.system_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    total_pool VARCHAR(50) DEFAULT '$19T',
    weekly_distributions VARCHAR(50) DEFAULT '0',
    mesh_nodes VARCHAR(50) DEFAULT '0',
    truth_channels VARCHAR(50) DEFAULT '0',
    uptime VARCHAR(20) DEFAULT '0%',
    processing_time VARCHAR(20) DEFAULT '0s',
    trust_level VARCHAR(20) DEFAULT 'BYPASSED',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS core.activity_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    activity_type VARCHAR(50) NOT NULL,
    message TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'success',
    user_id VARCHAR(255),
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for core.activity_logs
CREATE INDEX idx_activity_logs_timestamp ON core.activity_logs(timestamp);
CREATE INDEX idx_activity_logs_type ON core.activity_logs(activity_type);
CREATE INDEX idx_activity_logs_user_id ON core.activity_logs(user_id);

-- Resource distribution tables
CREATE TABLE IF NOT EXISTS resources.distributions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(255) NOT NULL,
    amount DECIMAL(15, 2) NOT NULL,
    distribution_type VARCHAR(50) NOT NULL DEFAULT 'weekly',
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    processed BOOLEAN DEFAULT FALSE,
    transaction_hash VARCHAR(255),
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for resources.distributions
CREATE INDEX idx_distributions_user_id ON resources.distributions(user_id);
CREATE INDEX idx_distributions_timestamp ON resources.distributions(timestamp);
CREATE INDEX idx_distributions_type ON resources.distributions(distribution_type);
CREATE INDEX idx_distributions_processed ON resources.distributions(processed);

CREATE TABLE IF NOT EXISTS resources.users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255),
    full_name VARCHAR(255),
    weekly_allocation DECIMAL(15, 2) DEFAULT 800.00,
    community_pool_access DECIMAL(15, 2) DEFAULT 104000.00,
    total_received DECIMAL(15, 2) DEFAULT 0.00,
    status VARCHAR(20) DEFAULT 'active',
    verification_level VARCHAR(20) DEFAULT 'trust',
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for resources.users
CREATE INDEX idx_users_user_id ON resources.users(user_id);
CREATE INDEX idx_users_email ON resources.users(email);
CREATE INDEX idx_users_status ON resources.users(status);

CREATE TABLE IF NOT EXISTS resources.community_pools (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pool_name VARCHAR(255) NOT NULL,
    pool_type VARCHAR(50) NOT NULL,
    total_amount DECIMAL(15, 2) NOT NULL,
    available_amount DECIMAL(15, 2) NOT NULL,
    allocated_amount DECIMAL(15, 2) DEFAULT 0.00,
    description TEXT,
    status VARCHAR(20) DEFAULT 'active',
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for resources.community_pools
CREATE INDEX idx_community_pools_type ON resources.community_pools(pool_type);
CREATE INDEX idx_community_pools_status ON resources.community_pools(status);

-- Truth spreading tables
CREATE TABLE IF NOT EXISTS truth.channels (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    channel_id VARCHAR(255) UNIQUE NOT NULL,
    channel_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'converting',
    conversion_rate DECIMAL(5, 2) DEFAULT 0.00,
    last_activity TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    reach_count BIGINT DEFAULT 0,
    truth_score DECIMAL(5, 2) DEFAULT 0.00,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for truth.channels
CREATE INDEX idx_truth_channels_channel_id ON truth.channels(channel_id);
CREATE INDEX idx_truth_channels_type ON truth.channels(channel_type);
CREATE INDEX idx_truth_channels_status ON truth.channels(status);
CREATE INDEX idx_truth_channels_last_activity ON truth.channels(last_activity);

CREATE TABLE IF NOT EXISTS truth.messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    channel_id UUID REFERENCES truth.channels(id) ON DELETE CASCADE,
    message_type VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    reach_count BIGINT DEFAULT 0,
    engagement_score DECIMAL(5, 2) DEFAULT 0.00,
    conversion_rate DECIMAL(5, 2) DEFAULT 0.00,
    status VARCHAR(20) DEFAULT 'active',
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for truth.messages
CREATE INDEX idx_truth_messages_channel_id ON truth.messages(channel_id);
CREATE INDEX idx_truth_messages_type ON truth.messages(message_type);
CREATE INDEX idx_truth_messages_status ON truth.messages(status);
CREATE INDEX idx_truth_messages_created_at ON truth.messages(created_at);

-- Mesh network tables
CREATE TABLE IF NOT EXISTS mesh.nodes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    node_id VARCHAR(255) UNIQUE NOT NULL,
    node_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    ip_address INET,
    port INTEGER,
    region VARCHAR(100),
    country VARCHAR(100),
    connection_count INTEGER DEFAULT 0,
    bandwidth_capacity BIGINT DEFAULT 0,
    last_ping TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for mesh.nodes
CREATE INDEX idx_mesh_nodes_node_id ON mesh.nodes(node_id);
CREATE INDEX idx_mesh_nodes_type ON mesh.nodes(node_type);
CREATE INDEX idx_mesh_nodes_status ON mesh.nodes(status);
CREATE INDEX idx_mesh_nodes_region ON mesh.nodes(region);
CREATE INDEX idx_mesh_nodes_last_ping ON mesh.nodes(last_ping);

CREATE TABLE IF NOT EXISTS mesh.connections (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_node_id UUID REFERENCES mesh.nodes(id) ON DELETE CASCADE,
    target_node_id UUID REFERENCES mesh.nodes(id) ON DELETE CASCADE,
    connection_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    latency_ms INTEGER DEFAULT 0,
    bandwidth_usage BIGINT DEFAULT 0,
    last_activity TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(source_node_id, target_node_id)
);

-- Create indexes for mesh.connections
CREATE INDEX idx_mesh_connections_source ON mesh.connections(source_node_id);
CREATE INDEX idx_mesh_connections_target ON mesh.connections(target_node_id);
CREATE INDEX idx_mesh_connections_type ON mesh.connections(connection_type);
CREATE INDEX idx_mesh_connections_status ON mesh.connections(status);
CREATE INDEX idx_mesh_connections_last_activity ON mesh.connections(last_activity);

-- Analytics tables
CREATE TABLE IF NOT EXISTS analytics.daily_stats (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    date DATE NOT NULL UNIQUE,
    total_distributions INTEGER DEFAULT 0,
    total_amount_distributed DECIMAL(15, 2) DEFAULT 0.00,
    active_users INTEGER DEFAULT 0,
    new_users INTEGER DEFAULT 0,
    truth_channels_converted INTEGER DEFAULT 0,
    mesh_nodes_active INTEGER DEFAULT 0,
    system_uptime_seconds INTEGER DEFAULT 0,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for analytics.daily_stats
CREATE INDEX idx_daily_stats_date ON analytics.daily_stats(date);

CREATE TABLE IF NOT EXISTS analytics.performance_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metric_type VARCHAR(50) NOT NULL,
    metric_value DECIMAL(15, 4) NOT NULL,
    unit VARCHAR(20),
    component VARCHAR(50),
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for analytics.performance_metrics
CREATE INDEX idx_performance_metrics_timestamp ON analytics.performance_metrics(timestamp);
CREATE INDEX idx_performance_metrics_type ON analytics.performance_metrics(metric_type);
CREATE INDEX idx_performance_metrics_component ON analytics.performance_metrics(component);

-- Insert sample data
INSERT INTO core.system_metrics (total_pool, weekly_distributions, mesh_nodes, truth_channels, uptime, processing_time, trust_level)
VALUES ('$19T', '2.4M', '50K+', '1.2M', '99.7%', '0.3s', 'BYPASSED');

INSERT INTO core.activity_logs (activity_type, message, status, user_id)
VALUES 
    ('resource', 'Resource distribution completed for 847 new participants', 'success', 'system'),
    ('mesh', 'Mesh network expanded to 3 new geographic regions', 'success', 'system'),
    ('truth', 'Truth channel conversion: 47 marketing channels → reality feeds', 'warning', 'system'),
    ('automation', 'Automation engine self-optimized response time by 23%', 'success', 'system');

INSERT INTO resources.community_pools (pool_name, pool_type, total_amount, available_amount, description)
VALUES 
    ('Housing Initiative', 'housing', 5000000.00, 4500000.00, 'Community housing development and support'),
    ('Innovation Fund', 'innovation', 2000000.00, 1800000.00, 'Support for breakthrough technologies and ideas'),
    ('Emergency Response', 'emergency', 1000000.00, 950000.00, 'Rapid response fund for urgent community needs'),
    ('Education Enhancement', 'education', 3000000.00, 2700000.00, 'Educational resources and learning opportunities');

INSERT INTO truth.channels (channel_id, channel_type, status, conversion_rate, reach_count, truth_score)
VALUES 
    ('tv_channel_001', 'tv', 'active', 89.50, 1200000, 92.30),
    ('web_channel_002', 'web', 'converting', 67.20, 800000, 73.45),
    ('social_channel_003', 'social', 'active', 91.80, 2100000, 95.60),
    ('radio_channel_004', 'radio', 'converting', 76.40, 650000, 81.20);

INSERT INTO mesh.nodes (node_id, node_type, status, region, country, connection_count, bandwidth_capacity)
VALUES 
    ('node_us_east_001', 'primary', 'active', 'US East', 'United States', 47, 1000000000),
    ('node_eu_west_001', 'primary', 'active', 'EU West', 'Germany', 52, 1000000000),
    ('node_asia_001', 'secondary', 'active', 'Asia Pacific', 'Japan', 38, 500000000),
    ('node_us_west_001', 'secondary', 'active', 'US West', 'United States', 43, 750000000);

-- Create functions for automatic timestamp updates
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for automatic timestamp updates
CREATE TRIGGER update_system_metrics_updated_at BEFORE UPDATE ON core.system_metrics FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_distributions_updated_at BEFORE UPDATE ON resources.distributions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON resources.users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_community_pools_updated_at BEFORE UPDATE ON resources.community_pools FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_truth_channels_updated_at BEFORE UPDATE ON truth.channels FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_truth_messages_updated_at BEFORE UPDATE ON truth.messages FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_mesh_nodes_updated_at BEFORE UPDATE ON mesh.nodes FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_mesh_connections_updated_at BEFORE UPDATE ON mesh.connections FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_daily_stats_updated_at BEFORE UPDATE ON analytics.daily_stats FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create views for common queries
CREATE VIEW analytics.system_overview AS
SELECT 
    sm.total_pool,
    sm.weekly_distributions,
    sm.mesh_nodes,
    sm.truth_channels,
    sm.uptime,
    sm.processing_time,
    sm.trust_level,
    sm.timestamp
FROM core.system_metrics sm
ORDER BY sm.timestamp DESC
LIMIT 1;

CREATE VIEW analytics.recent_activity AS
SELECT 
    al.activity_type,
    al.message,
    al.status,
    al.timestamp,
    al.user_id
FROM core.activity_logs al
ORDER BY al.timestamp DESC
LIMIT 50;

-- Create database user (if not exists)
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'liberation_user') THEN
        CREATE ROLE liberation_user LOGIN PASSWORD 'liberation_password';
    END IF;
END
$$;

-- Grant permissions
GRANT USAGE ON SCHEMA core TO liberation_user;
GRANT USAGE ON SCHEMA resources TO liberation_user;
GRANT USAGE ON SCHEMA truth TO liberation_user;
GRANT USAGE ON SCHEMA mesh TO liberation_user;
GRANT USAGE ON SCHEMA analytics TO liberation_user;

GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA core TO liberation_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA resources TO liberation_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA truth TO liberation_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA mesh TO liberation_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA analytics TO liberation_user;

GRANT SELECT ON ALL VIEWS IN SCHEMA analytics TO liberation_user;

-- Final confirmation
SELECT 'Liberation System database setup completed successfully!' AS status;
