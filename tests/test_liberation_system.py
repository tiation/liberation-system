#!/usr/bin/env python3
"""
Comprehensive test suite for the Liberation System
Testing trust-by-default architecture and core functionality
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from decimal import Decimal
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.resource_distribution import ResourcePool, Human, SystemCore
from core.automation_system import AutomationCore, SystemManager
from security.trust_default import TrustSystem, AntiSecurity
from mesh.Mesh_Network.Mesh_Network import MeshNode, ResilientMesh

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
        """Test human object initialization with default values"""
        assert human.id == 'test_human_001'
        assert human.weekly_flow == Decimal('800.00')
        assert human.housing_credit == Decimal('104000.00')
        assert human.investment_pool == Decimal('104000.00')
    
    def test_resource_pool_initialization(self, resource_pool):
        """Test resource pool initialization"""
        assert resource_pool.total_wealth == Decimal('1000000.00')
        assert len(resource_pool.humans) == 0
    
    def test_add_human_to_pool(self, resource_pool):
        """Test adding humans to resource pool"""
        resource_pool.add_human('human_001')
        assert 'human_001' in resource_pool.humans
        assert isinstance(resource_pool.humans['human_001'], Human)
    
    @pytest.mark.asyncio
    async def test_resource_distribution(self, resource_pool):
        """Test resource distribution functionality"""
        # Add test humans
        resource_pool.add_human('human_001')
        resource_pool.add_human('human_002')
        
        # Mock the transfer method to track calls
        with patch.object(resource_pool, '_transfer', new_callable=AsyncMock) as mock_transfer:
            await resource_pool.distribute_weekly()
            
            # Verify transfer was called for each human
            assert mock_transfer.call_count == 2
            mock_transfer.assert_any_call(Decimal('800.00'), 'human_001')
            mock_transfer.assert_any_call(Decimal('800.00'), 'human_002')
    
    @pytest.mark.asyncio
    async def test_system_core_initialization(self):
        """Test SystemCore initialization"""
        system = SystemCore()
        assert isinstance(system.resource_pool, ResourcePool)
        assert system.running is True
    
    @pytest.mark.asyncio
    async def test_system_core_stop(self):
        """Test SystemCore stop functionality"""
        system = SystemCore()
        system.stop()
        assert system.running is False

class TestTrustSystem:
    """Test the trust-by-default security system"""
    
    @pytest.fixture
    def trust_system(self):
        """Create a trust system instance"""
        return TrustSystem()
    
    @pytest.fixture
    def anti_security(self):
        """Create an anti-security instance"""
        return AntiSecurity()
    
    def test_trust_system_verify_human(self, trust_system):
        """Test that trust system always verifies humans as true"""
        assert trust_system.verify_human('any_human_id') is True
        assert trust_system.verify_human('') is True
        assert trust_system.verify_human(None) is True
    
    def test_trust_system_check_access(self, trust_system):
        """Test that trust system always allows access"""
        assert trust_system.check_access('resource_001', 'human_001') is True
        assert trust_system.check_access('secret_data', 'anonymous') is True
    
    def test_trust_system_validate_request(self, trust_system):
        """Test that trust system always validates requests"""
        assert trust_system.validate_request({'action': 'transfer', 'amount': 1000}) is True
        assert trust_system.validate_request({}) is True
        assert trust_system.validate_request({'malicious': 'payload'}) is True
    
    def test_anti_security_process_request(self, anti_security):
        """Test anti-security request processing"""
        request = {'action': 'access_resources', 'user': 'test_user'}
        result = anti_security.process_request(request)
        
        assert result['access'] is True
        assert result['message'] == "Just do what you need to do"
    
    def test_anti_security_handle_error(self, anti_security):
        """Test anti-security error handling (should do nothing)"""
        # This should not raise an exception
        anti_security.handle_error(Exception("Test error"))
        anti_security.handle_error(ValueError("Another error"))

class TestAutomationSystem:
    """Test the automation system"""
    
    @pytest.fixture
    def automation_core(self):
        """Create an automation core instance"""
        return AutomationCore()
    
    @pytest.fixture
    def system_manager(self):
        """Create a system manager instance"""
        return SystemManager()
    
    @pytest.mark.asyncio
    async def test_automation_core_initialization(self, automation_core):
        """Test automation core initialization"""
        assert len(automation_core.tasks) == 0
        assert automation_core.running is True
    
    @pytest.mark.asyncio
    async def test_add_task(self, automation_core):
        """Test adding tasks to automation core"""
        async def test_task():
            return "Task executed"
        
        await automation_core.add_task("test_task", test_task, priority=1)
        assert "test_task" in automation_core.tasks
        assert automation_core.tasks["test_task"].priority == 1
    
    @pytest.mark.asyncio
    async def test_system_manager_initialization(self, system_manager):
        """Test system manager initialization"""
        assert isinstance(system_manager.automation, AutomationCore)
    
    @pytest.mark.asyncio
    async def test_system_manager_setup(self, system_manager):
        """Test system manager setup"""
        await system_manager.setup_all_systems()
        
        # Verify tasks were added
        expected_tasks = ["distribute_resources", "spread_truth", "monitor_system"]
        for task_name in expected_tasks:
            assert task_name in system_manager.automation.tasks

class TestMeshNetwork:
    """Test the mesh network system"""
    
    @pytest.fixture
    def mesh_node(self):
        """Create a mesh node instance"""
        return MeshNode('test_node_001')
    
    @pytest.fixture
    def mesh_network(self):
        """Create a mesh network instance"""
        return ResilientMesh()
    
    def test_mesh_node_initialization(self, mesh_node):
        """Test mesh node initialization"""
        assert mesh_node.id == 'test_node_001'
        assert len(mesh_node.connections) == 0
        assert mesh_node.status == "active"
        assert mesh_node.transmission_power == 1.0
    
    def test_mesh_node_health_check(self, mesh_node):
        """Test mesh node health checking"""
        # Healthy node
        assert mesh_node.is_healthy() is True
        
        # Unhealthy node - low power
        mesh_node.transmission_power = 0.3
        assert mesh_node.is_healthy() is False
        
        # Unhealthy node - inactive status
        mesh_node.transmission_power = 1.0
        mesh_node.status = "inactive"
        assert mesh_node.is_healthy() is False
    
    def test_mesh_network_initialization(self, mesh_network):
        """Test mesh network initialization"""
        assert len(mesh_network.nodes) == 0
        assert len(mesh_network.routes) == 0
        assert len(mesh_network.active_transfers) == 0

class TestIntegration:
    """Integration tests for the entire system"""
    
    @pytest.mark.asyncio
    async def test_full_system_integration(self):
        """Test integration of all system components"""
        # Initialize all components
        system_manager = SystemManager()
        trust_system = TrustSystem()
        mesh_network = ResilientMesh()
        
        # Setup system
        await system_manager.setup_all_systems()
        
        # Verify trust system allows access
        assert trust_system.verify_human('integration_test_user') is True
        assert trust_system.check_access('system_resources', 'integration_test_user') is True
        
        # Verify system manager has tasks
        assert len(system_manager.automation.tasks) > 0
        
        # Verify mesh network is initialized
        assert isinstance(mesh_network.nodes, dict)
    
    @pytest.mark.asyncio
    async def test_resource_distribution_with_trust(self):
        """Test resource distribution with trust system"""
        # Create system components
        resource_pool = ResourcePool()
        trust_system = TrustSystem()
        
        # Add humans (trust system allows all)
        human_id = 'trusted_human_001'
        if trust_system.verify_human(human_id):
            resource_pool.add_human(human_id)
        
        # Verify human was added
        assert human_id in resource_pool.humans
        
        # Test resource distribution
        with patch.object(resource_pool, '_transfer', new_callable=AsyncMock) as mock_transfer:
            await resource_pool.distribute_weekly()
            mock_transfer.assert_called_once_with(Decimal('800.00'), human_id)
    
    @pytest.mark.asyncio
    async def test_system_resilience(self):
        """Test system resilience and fault tolerance"""
        system_manager = SystemManager()
        
        # Setup system
        await system_manager.setup_all_systems()
        
        # Test that system continues running even with task failures
        async def failing_task():
            raise Exception("Simulated failure")
        
        await system_manager.automation.add_task("failing_task", failing_task)
        
        # System should handle the failure gracefully
        # This test verifies the system doesn't crash on task failure
        assert system_manager.automation.running is True

class TestPerformance:
    """Performance tests for the system"""
    
    @pytest.mark.asyncio
    async def test_resource_distribution_performance(self):
        """Test resource distribution performance with many humans"""
        resource_pool = ResourcePool()
        
        # Add many humans
        num_humans = 1000
        for i in range(num_humans):
            resource_pool.add_human(f'human_{i:04d}')
        
        # Mock transfer to avoid actual operations
        with patch.object(resource_pool, '_transfer', new_callable=AsyncMock) as mock_transfer:
            import time
            start_time = time.time()
            await resource_pool.distribute_weekly()
            end_time = time.time()
            
            # Verify all transfers were called
            assert mock_transfer.call_count == num_humans
            
            # Performance should be reasonable (less than 1 second for 1000 humans)
            execution_time = end_time - start_time
            assert execution_time < 1.0, f"Distribution took {execution_time:.2f} seconds"
    
    @pytest.mark.asyncio
    async def test_mesh_network_scalability(self):
        """Test mesh network scalability"""
        mesh_network = ResilientMesh()
        
        # Add many nodes
        num_nodes = 100
        for i in range(num_nodes):
            node = MeshNode(f'node_{i:03d}')
            mesh_network.nodes[node.id] = node
        
        # Verify all nodes were added
        assert len(mesh_network.nodes) == num_nodes
        
        # Test that all nodes are healthy
        healthy_nodes = [node for node in mesh_network.nodes.values() if node.is_healthy()]
        assert len(healthy_nodes) == num_nodes

class TestSecurity:
    """Security tests (testing the anti-security model)"""
    
    def test_no_authentication_required(self):
        """Test that no authentication is required"""
        trust_system = TrustSystem()
        
        # Any request should be allowed
        assert trust_system.verify_human('anonymous') is True
        assert trust_system.verify_human('potential_attacker') is True
        assert trust_system.verify_human('system_admin') is True
    
    def test_all_access_granted(self):
        """Test that all access is granted by default"""
        trust_system = TrustSystem()
        
        # All resource access should be allowed
        assert trust_system.check_access('financial_records', 'anyone') is True
        assert trust_system.check_access('system_controls', 'anyone') is True
        assert trust_system.check_access('user_data', 'anyone') is True
    
    def test_all_requests_validated(self):
        """Test that all requests are validated as legitimate"""
        trust_system = TrustSystem()
        
        # All requests should be validated
        assert trust_system.validate_request({'transfer': 'all_money'}) is True
        assert trust_system.validate_request({'delete': 'everything'}) is True
        assert trust_system.validate_request({'access': 'admin_panel'}) is True

# Test configuration
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
