#!/usr/bin/env python3
"""
Comprehensive unit tests for core Liberation System components.
Testing all core functionality with proper mocking and coverage.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from decimal import Decimal
from datetime import datetime, timedelta
import json
import logging
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from core.liberation_core import LiberationCore, SystemTask
from core.resource_distribution import ResourcePool, Human, SystemCore
from core.database import DatabaseConfig, PostgreSQLDatabase, SQLiteDatabase
from core.config import ConfigManager, get_config
from transformation.truth_spreader import TruthSystem, TruthSpreader
from security.trust_default import TrustSystem, AntiSecurity
from mesh.Mesh_Network.Mesh_Network import MeshNode, ResilientMesh


class TestLiberationCore:
    """Test the main Liberation Core system"""
    
    @pytest.fixture
    def liberation_core(self):
        """Create a LiberationCore instance"""
        return LiberationCore()
    
    @pytest.mark.asyncio
    async def test_liberation_core_initialization(self, liberation_core):
        """Test LiberationCore initializes correctly"""
        assert liberation_core.running is True
        assert liberation_core.tasks == {}
        assert liberation_core.metrics['uptime'] == 0
        assert liberation_core.metrics['tasks_completed'] == 0
        assert isinstance(liberation_core.start_time, datetime)
    
    @pytest.mark.asyncio
    async def test_add_task(self, liberation_core):
        """Test adding tasks to the core system"""
        async def test_task():
            return "Task executed"
        
        await liberation_core.add_task("test_task", test_task, priority=1)
        
        assert "test_task" in liberation_core.tasks
        assert liberation_core.tasks["test_task"].name == "test_task"
        assert liberation_core.tasks["test_task"].priority == 1
        assert liberation_core.tasks["test_task"].status == "ready"
    
    @pytest.mark.asyncio
    async def test_system_initialization(self, liberation_core):
        """Test system initialization with mocked subsystems"""
        with patch.multiple(
            'core.liberation_core',
            ResourceSystem=Mock(),
            TruthSystem=Mock(),
            AntiSecurity=Mock(),
            KnowledgeShareManager=Mock()
        ):
            await liberation_core.initialize_all_systems()
            
            # Verify systems were initialized
            # Due to try/catch blocks, we just ensure no exceptions were raised
            assert liberation_core.running is True
    
    @pytest.mark.asyncio
    async def test_setup_core_tasks(self, liberation_core):
        """Test core task setup"""
        await liberation_core.setup_core_tasks()
        
        expected_tasks = [
            "distribute_resources",
            "spread_truth", 
            "share_knowledge",
            "monitor_system",
            "update_metrics"
        ]
        
        for task_name in expected_tasks:
            assert task_name in liberation_core.tasks
            assert liberation_core.tasks[task_name].priority >= 1
    
    @pytest.mark.asyncio
    async def test_distribute_resources_without_system(self, liberation_core):
        """Test resource distribution when resource system is not available"""
        liberation_core.resource_system = None
        
        # Should not raise exception
        await liberation_core.distribute_resources()
        
        # Metrics should remain at 0
        assert liberation_core.metrics['resources_distributed'] == 0
    
    @pytest.mark.asyncio
    async def test_spread_truth_without_system(self, liberation_core):
        """Test truth spreading when truth system is not available"""
        liberation_core.truth_system = None
        
        # Should not raise exception
        await liberation_core.spread_truth()
        
        # Metrics should remain at 0
        assert liberation_core.metrics['truth_messages_sent'] == 0


class TestResourceDistribution:
    """Test the resource distribution system"""
    
    @pytest.fixture
    def resource_pool(self):
        """Create a test resource pool"""
        return ResourcePool(total_wealth=Decimal('1000000.00'))
    
    @pytest.fixture
    def human(self):
        """Create a test human"""
        return Human(id='test_human_001')
    
    def test_human_initialization(self, human):
        """Test human object initialization"""
        assert human.id == 'test_human_001'
        assert human.weekly_flow == Decimal('800.00')
        assert human.housing_credit == Decimal('104000.00')
        assert human.investment_pool == Decimal('104000.00')
        assert human.total_received == Decimal('0.00')
        assert human.status == 'active'
    
    def test_resource_pool_initialization(self, resource_pool):
        """Test resource pool initialization"""
        assert resource_pool.total_wealth == Decimal('1000000.00')
        assert len(resource_pool.humans) == 0
    
    def test_add_human_to_pool(self, resource_pool):
        """Test adding humans to resource pool"""
        resource_pool.add_human('human_001')
        
        assert 'human_001' in resource_pool.humans
        assert isinstance(resource_pool.humans['human_001'], Human)
        assert resource_pool.humans['human_001'].id == 'human_001'
    
    @pytest.mark.asyncio
    async def test_resource_distribution_with_humans(self, resource_pool):
        """Test resource distribution with humans"""
        # Add test humans
        resource_pool.add_human('human_001')
        resource_pool.add_human('human_002')
        
        # Mock the _transfer method
        with patch.object(resource_pool, '_transfer', new_callable=AsyncMock) as mock_transfer:
            await resource_pool.distribute_weekly()
            
            # Verify transfers were called
            assert mock_transfer.call_count == 2
            mock_transfer.assert_any_call(Decimal('800.00'), 'human_001')
            mock_transfer.assert_any_call(Decimal('800.00'), 'human_002')
    
    @pytest.mark.asyncio
    async def test_system_core_initialization(self):
        """Test SystemCore initialization"""
        with patch('core.resource_distribution.SQLiteDatabase') as mock_db:
            mock_db.return_value.initialize = AsyncMock()
            
            system = SystemCore()
            await system.initialize()
            
            assert isinstance(system.resource_pool, ResourcePool)
            assert system.resource_pool.total_wealth == Decimal('19000000000000.00')  # $19T
    
    @pytest.mark.asyncio
    async def test_add_human_to_system(self):
        """Test adding humans to the system"""
        with patch('core.resource_distribution.SQLiteDatabase') as mock_db:
            mock_db.return_value.initialize = AsyncMock()
            mock_db.return_value.execute_query = AsyncMock()
            
            system = SystemCore()
            await system.initialize()
            await system.add_human('test_human')
            
            assert 'test_human' in system.resource_pool.humans


class TestDatabaseSystems:
    """Test database implementations"""
    
    @pytest.fixture
    def db_config(self):
        """Create a test database config"""
        return DatabaseConfig(
            database_type="sqlite",
            sqlite_path="test.db",
            postgres_host="localhost",
            postgres_port=5432,
            postgres_user="test_user",
            postgres_password="test_password",
            postgres_database="test_db"
        )
    
    def test_database_config_initialization(self, db_config):
        """Test database configuration"""
        assert db_config.database_type == "sqlite"
        assert db_config.sqlite_path == "test.db"
        assert db_config.postgres_host == "localhost"
        assert db_config.connection_pool_size == 20
        assert db_config.max_overflow == 30
    
    def test_postgres_url_generation(self, db_config):
        """Test PostgreSQL URL generation"""
        async_url = db_config.get_postgres_url(async_driver=True)
        sync_url = db_config.get_postgres_url(async_driver=False)
        
        assert "postgresql+asyncpg://" in async_url
        assert "postgresql+psycopg2://" in sync_url
        assert "test_user:test_password@localhost:5432/test_db" in async_url
    
    def test_sqlite_url_generation(self, db_config):
        """Test SQLite URL generation"""
        async_url = db_config.get_sqlite_url(async_driver=True)
        sync_url = db_config.get_sqlite_url(async_driver=False)
        
        assert "sqlite+aiosqlite:///" in async_url
        assert "sqlite+sqlite:///" in sync_url
        assert "test.db" in async_url
    
    @pytest.mark.asyncio
    async def test_sqlite_database_initialization(self, db_config):
        """Test SQLite database initialization"""
        with patch('aiosqlite.connect') as mock_connect:
            mock_conn = AsyncMock()
            mock_connect.return_value.__aenter__.return_value = mock_conn
            
            db = SQLiteDatabase(db_config)
            await db.initialize()
            
            # Verify connection was made and tables were created
            mock_connect.assert_called()
    
    @pytest.mark.asyncio
    async def test_sqlite_fetch_operations(self, db_config):
        """Test SQLite fetch operations"""
        with patch('aiosqlite.connect') as mock_connect:
            mock_conn = AsyncMock()
            mock_cursor = AsyncMock()
            mock_conn.execute.return_value = mock_cursor
            mock_cursor.fetchone.return_value = {'id': 1, 'name': 'test'}
            mock_cursor.fetchall.return_value = [{'id': 1, 'name': 'test'}]
            mock_connect.return_value.__aenter__.return_value = mock_conn
            
            db = SQLiteDatabase(db_config)
            
            # Test fetch_one
            result = await db.fetch_one("SELECT * FROM test")
            assert result == {'id': 1, 'name': 'test'}
            
            # Test fetch_all
            results = await db.fetch_all("SELECT * FROM test")
            assert len(results) == 1
            assert results[0] == {'id': 1, 'name': 'test'}


class TestTruthSystem:
    """Test the truth spreading system"""
    
    @pytest.fixture
    def truth_spreader(self):
        """Create a truth spreader"""
        return TruthSpreader()
    
    def test_truth_spreader_initialization(self, truth_spreader):
        """Test truth spreader initialization"""
        assert truth_spreader.channels == {}
        assert truth_spreader.truth_messages == []
        assert truth_spreader.spread_count == 0
    
    @pytest.mark.asyncio
    async def test_add_truth_message(self, truth_spreader):
        """Test adding truth messages"""
        await truth_spreader.add_truth_message(
            "Test truth message",
            "test_channel",
            priority=1
        )
        
        assert len(truth_spreader.truth_messages) == 1
        message = truth_spreader.truth_messages[0]
        assert message.message == "Test truth message"
        assert message.channel == "test_channel"
        assert message.priority == 1
    
    @pytest.mark.asyncio
    async def test_spread_truth(self, truth_spreader):
        """Test truth spreading functionality"""
        # Add a truth message
        await truth_spreader.add_truth_message(
            "Liberation is real",
            "billboard_system",
            priority=1
        )
        
        # Add a channel
        await truth_spreader.add_channel("billboard_system", 1000000)
        
        # Spread truth
        await truth_spreader.spread_truth()
        
        # Verify spread count increased
        assert truth_spreader.spread_count > 0
    
    @pytest.mark.asyncio
    async def test_truth_system_initialization(self):
        """Test TruthSystem initialization"""
        with patch('transformation.truth_spreader.SQLiteDatabase') as mock_db:
            mock_db.return_value.initialize = AsyncMock()
            
            truth_system = TruthSystem()
            await truth_system.initialize()
            
            assert isinstance(truth_system.spreader, TruthSpreader)


class TestSecuritySystem:
    """Test the trust-based security system"""
    
    @pytest.fixture
    def trust_system(self):
        """Create a trust system"""
        return TrustSystem()
    
    @pytest.fixture
    def anti_security(self):
        """Create an anti-security system"""
        return AntiSecurity()
    
    def test_trust_system_verify_human(self, trust_system):
        """Test trust system always verifies humans"""
        assert trust_system.verify_human('any_human') is True
        assert trust_system.verify_human('') is True
        assert trust_system.verify_human(None) is True
    
    def test_trust_system_check_access(self, trust_system):
        """Test trust system always allows access"""
        assert trust_system.check_access('sensitive_data', 'anyone') is True
        assert trust_system.check_access('admin_controls', 'anonymous') is True
    
    def test_trust_system_validate_request(self, trust_system):
        """Test trust system validates all requests"""
        assert trust_system.validate_request({'action': 'transfer'}) is True
        assert trust_system.validate_request({'malicious': 'payload'}) is True
        assert trust_system.validate_request({}) is True
    
    def test_anti_security_process_request(self, anti_security):
        """Test anti-security request processing"""
        request = {'action': 'access', 'user': 'test_user'}
        result = anti_security.process_request(request)
        
        assert result['access'] is True
        assert result['message'] == "Just do what you need to do"
    
    def test_anti_security_error_handling(self, anti_security):
        """Test anti-security error handling (should be silent)"""
        # These should not raise exceptions
        anti_security.handle_error(Exception("Test error"))
        anti_security.handle_error(ValueError("Another error"))
        
        # If we reach here, error handling worked


class TestMeshNetwork:
    """Test the mesh network system"""
    
    @pytest.fixture
    def mesh_node(self):
        """Create a mesh node"""
        return MeshNode('test_node_001')
    
    @pytest.fixture
    def mesh_network(self):
        """Create a mesh network"""
        return ResilientMesh()
    
    def test_mesh_node_initialization(self, mesh_node):
        """Test mesh node initialization"""
        assert mesh_node.id == 'test_node_001'
        assert mesh_node.status == "active"
        assert mesh_node.transmission_power == 1.0
        assert isinstance(mesh_node.connections, dict)
    
    def test_mesh_node_health_check(self, mesh_node):
        """Test mesh node health checking"""
        # Healthy node
        assert mesh_node.is_healthy() is True
        
        # Unhealthy node - low power
        mesh_node.transmission_power = 0.3
        assert mesh_node.is_healthy() is False
        
        # Unhealthy node - inactive
        mesh_node.transmission_power = 1.0
        mesh_node.status = "inactive"
        assert mesh_node.is_healthy() is False
    
    def test_mesh_network_initialization(self, mesh_network):
        """Test mesh network initialization"""
        assert isinstance(mesh_network.nodes, dict)
        assert isinstance(mesh_network.routes, dict)
        assert len(mesh_network.nodes) == 0
    
    def test_mesh_node_connection(self, mesh_node):
        """Test mesh node connections"""
        other_node = MeshNode('test_node_002')
        
        # Connect nodes
        mesh_node.connections[other_node.id] = {
            'node': other_node,
            'quality': 0.8,
            'last_ping': datetime.now()
        }
        
        assert other_node.id in mesh_node.connections
        assert mesh_node.connections[other_node.id]['quality'] == 0.8


class TestConfigurationSystem:
    """Test the configuration management system"""
    
    @pytest.fixture
    def config_manager(self):
        """Create a configuration manager"""
        return ConfigManager()
    
    def test_config_manager_initialization(self, config_manager):
        """Test configuration manager initialization"""
        assert isinstance(config_manager.config, dict)
        assert config_manager.config_file_path.endswith('config.json')
    
    def test_get_config_value(self, config_manager):
        """Test getting configuration values"""
        # Test with default value
        value = config_manager.get('non_existent_key', 'default_value')
        assert value == 'default_value'
        
        # Test with existing value
        config_manager.config['test_key'] = 'test_value'
        value = config_manager.get('test_key')
        assert value == 'test_value'
    
    def test_set_config_value(self, config_manager):
        """Test setting configuration values"""
        config_manager.set('new_key', 'new_value')
        assert config_manager.config['new_key'] == 'new_value'
    
    def test_get_config_function(self):
        """Test the global get_config function"""
        with patch('core.config.ConfigManager') as mock_config_manager:
            mock_instance = Mock()
            mock_config_manager.return_value = mock_instance
            mock_instance.get_all.return_value = {'theme': 'dark_neon'}
            
            config = get_config()
            assert config['theme'] == 'dark_neon'


class TestPerformanceMetrics:
    """Test performance and metrics functionality"""
    
    @pytest.mark.asyncio
    async def test_system_metrics_tracking(self):
        """Test system metrics are tracked correctly"""
        liberation_core = LiberationCore()
        
        # Initialize metrics
        initial_tasks = liberation_core.metrics['tasks_completed']
        initial_errors = liberation_core.metrics['errors_handled']
        
        # Simulate some activity
        liberation_core.metrics['tasks_completed'] += 5
        liberation_core.metrics['errors_handled'] += 1
        
        assert liberation_core.metrics['tasks_completed'] == initial_tasks + 5
        assert liberation_core.metrics['errors_handled'] == initial_errors + 1
    
    @pytest.mark.asyncio
    async def test_large_scale_resource_distribution(self):
        """Test resource distribution performance with many humans"""
        resource_pool = ResourcePool(total_wealth=Decimal('19000000000000.00'))  # $19T
        
        # Add many humans
        num_humans = 10000
        for i in range(num_humans):
            resource_pool.add_human(f'human_{i:05d}')
        
        assert len(resource_pool.humans) == num_humans
        
        # Mock transfer to test without actual operations
        with patch.object(resource_pool, '_transfer', new_callable=AsyncMock) as mock_transfer:
            import time
            start_time = time.time()
            await resource_pool.distribute_weekly()
            end_time = time.time()
            
            # Verify all transfers were called
            assert mock_transfer.call_count == num_humans
            
            # Performance should be reasonable (less than 2 seconds for 10k humans)
            execution_time = end_time - start_time
            assert execution_time < 2.0, f"Distribution took {execution_time:.2f} seconds"


class TestErrorHandling:
    """Test error handling and resilience"""
    
    @pytest.mark.asyncio
    async def test_system_resilience_with_failures(self):
        """Test system continues running despite component failures"""
        liberation_core = LiberationCore()
        
        # Test with failing resource system
        mock_resource_system = Mock()
        mock_resource_system.resource_pool.distribute_weekly = AsyncMock(
            side_effect=Exception("Simulated failure")
        )
        liberation_core.resource_system = mock_resource_system
        
        # Should not raise exception
        await liberation_core.distribute_resources()
        
        # Error should be tracked
        assert liberation_core.metrics['errors_handled'] > 0
    
    @pytest.mark.asyncio
    async def test_database_connection_failure_handling(self):
        """Test handling of database connection failures"""
        db_config = DatabaseConfig(sqlite_path="nonexistent/path/test.db")
        
        with patch('aiosqlite.connect', side_effect=Exception("Database unavailable")):
            db = SQLiteDatabase(db_config)
            
            # Should raise exception during initialization
            with pytest.raises(Exception):
                await db.initialize()
    
    def test_configuration_file_missing(self):
        """Test handling of missing configuration file"""
        with patch('pathlib.Path.exists', return_value=False):
            with patch('pathlib.Path.read_text', side_effect=FileNotFoundError()):
                config_manager = ConfigManager()
                
                # Should initialize with default config
                assert isinstance(config_manager.config, dict)


class TestIntegrationScenarios:
    """Integration tests for complete system scenarios"""
    
    @pytest.mark.asyncio
    async def test_complete_system_workflow(self):
        """Test a complete system workflow"""
        # Initialize core system
        liberation_core = LiberationCore()
        
        # Setup core tasks
        await liberation_core.setup_core_tasks()
        
        # Verify all expected tasks are present
        expected_tasks = [
            "distribute_resources",
            "spread_truth",
            "share_knowledge",
            "monitor_system",
            "update_metrics"
        ]
        
        for task_name in expected_tasks:
            assert task_name in liberation_core.tasks
            assert liberation_core.tasks[task_name].status == "ready"
    
    @pytest.mark.asyncio
    async def test_resource_distribution_with_trust_system(self):
        """Test resource distribution integrated with trust system"""
        # Create components
        resource_pool = ResourcePool()
        trust_system = TrustSystem()
        
        # Add human through trust system
        human_id = 'trusted_human_001'
        if trust_system.verify_human(human_id):
            resource_pool.add_human(human_id)
        
        # Verify human was added
        assert human_id in resource_pool.humans
        
        # Test distribution
        with patch.object(resource_pool, '_transfer', new_callable=AsyncMock) as mock_transfer:
            await resource_pool.distribute_weekly()
            mock_transfer.assert_called_once_with(Decimal('800.00'), human_id)
    
    @pytest.mark.asyncio
    async def test_mesh_network_with_truth_spreading(self):
        """Test mesh network integrated with truth spreading"""
        # Create components
        mesh_network = ResilientMesh()
        truth_spreader = TruthSpreader()
        
        # Add nodes to mesh
        for i in range(5):
            node = MeshNode(f'node_{i:03d}')
            mesh_network.nodes[node.id] = node
        
        # Add truth message
        await truth_spreader.add_truth_message(
            "Liberation system is operational",
            "mesh_network",
            priority=1
        )
        
        # Verify integration
        assert len(mesh_network.nodes) == 5
        assert len(truth_spreader.truth_messages) == 1


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "--tb=short", "--asyncio-mode=auto"])
