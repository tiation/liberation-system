#!/usr/bin/env python3
"""
Liberation System Integration Test
Tests all major components working together
"""

import asyncio
import logging
import sys
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# Add project root to path for imports
sys.path.append(str(Path(__file__).parent))

from core.resource_distribution import SystemCore as ResourceCore
from core.automation_system import SystemManager as AutomationManager
from security.trust_default import AntiSecurity

console = Console()

class IntegrationTest:
    def __init__(self):
        self.console = Console()
        self.tests_passed = 0
        self.tests_failed = 0
        self.results = []
        
    async def run_all_tests(self):
        """Run comprehensive integration tests"""
        
        self.console.print(Panel.fit("🧪 Liberation System Integration Tests", style="bold blue"))
        
        # Test 1: Resource Distribution System
        await self.test_resource_distribution()
        
        # Test 2: Automation System
        await self.test_automation_system()
        
        # Test 3: Security System
        await self.test_security_system()
        
        # Test 4: Database Operations
        await self.test_database_operations()
        
        # Test 5: Error Handling
        await self.test_error_handling()
        
        # Test 6: Performance Test
        await self.test_performance()
        
        # Display results
        self.display_results()
        
    async def test_resource_distribution(self):
        """Test resource distribution system"""
        test_name = "Resource Distribution System"
        try:
            self.console.print(f"\n🔄 Testing {test_name}...")
            
            # Initialize system
            system = ResourceCore()
            await system.initialize()
            
            # Add test humans
            test_humans = [f"human_{i:06d}" for i in range(1, 6)]
            for human_id in test_humans:
                await system.add_human(human_id)
            
            # Run distribution
            await system.resource_pool.distribute_weekly()
            
            # Check statistics
            stats = await system.get_system_stats()
            
            # Validation
            assert stats['total_humans'] == 5
            assert stats['total_distributed'] > 0
            assert stats['active_humans'] == 5
            
            self.record_test_result(test_name, True, "All resource distribution tests passed")
            
        except Exception as e:
            self.record_test_result(test_name, False, f"Error: {str(e)}")
    
    async def test_automation_system(self):
        """Test automation system"""
        test_name = "Automation System"
        try:
            self.console.print(f"\n🔄 Testing {test_name}...")
            
            # Initialize automation manager
            manager = AutomationManager()
            await manager.initialize()
            await manager.setup_all_systems()
            
            # Run tasks once
            for task in manager.automation.tasks.values():
                await manager.automation._run_task(task)
            
            # Check task statistics
            stats = await manager.automation.get_task_statistics()
            
            # Validation
            assert stats['total_tasks'] == 5
            assert stats['total_runs'] > 0
            assert stats['success_rate'] > 0
            
            self.record_test_result(test_name, True, "All automation tests passed")
            
        except Exception as e:
            self.record_test_result(test_name, False, f"Error: {str(e)}")
    
    async def test_security_system(self):
        """Test security system"""
        test_name = "Security System"
        try:
            self.console.print(f"\n🔄 Testing {test_name}...")
            
            # Initialize security system
            security = AntiSecurity()
            
            # Test valid request
            valid_request = {
                "human_id": "human_000001",
                "resource_id": "resource_test",
                "action": "access"
            }
            
            response = security.process_request(valid_request)
            assert response['access'] == True
            
            # Test invalid request
            invalid_request = {
                "human_id": "invalid_human",
                "resource_id": "resource_test",
                "action": "access"
            }
            
            response = security.process_request(invalid_request)
            assert response['access'] == False
            
            self.record_test_result(test_name, True, "All security tests passed")
            
        except Exception as e:
            self.record_test_result(test_name, False, f"Error: {str(e)}")
    
    async def test_database_operations(self):
        """Test database operations"""
        test_name = "Database Operations"
        try:
            self.console.print(f"\n🔄 Testing {test_name}...")
            
            # Test resource database
            system = ResourceCore()
            await system.initialize()
            
            # Add and verify human
            human_id = "human_test_001"
            await system.add_human(human_id)
            
            # Verify human exists
            assert human_id in system.resource_pool.humans
            
            # Test transaction logging
            await system.resource_pool._transfer(100.0, human_id)
            
            self.record_test_result(test_name, True, "All database tests passed")
            
        except Exception as e:
            self.record_test_result(test_name, False, f"Error: {str(e)}")
    
    async def test_error_handling(self):
        """Test error handling capabilities"""
        test_name = "Error Handling"
        try:
            self.console.print(f"\n🔄 Testing {test_name}...")
            
            # Test resource system error handling
            system = ResourceCore()
            await system.initialize()
            
            # Try to add invalid human (should handle gracefully)
            result = await system.add_human("")
            assert result == False  # Should fail gracefully
            
            # Test security error handling
            security = AntiSecurity()
            invalid_request = {}  # Missing required fields
            
            response = security.process_request(invalid_request)
            assert response['access'] == False
            
            self.record_test_result(test_name, True, "All error handling tests passed")
            
        except Exception as e:
            self.record_test_result(test_name, False, f"Error: {str(e)}")
    
    async def test_performance(self):
        """Test system performance"""
        test_name = "Performance Test"
        try:
            self.console.print(f"\n🔄 Testing {test_name}...")
            
            import time
            
            # Test resource distribution performance
            system = ResourceCore()
            await system.initialize()
            
            # Add multiple humans
            start_time = time.time()
            for i in range(1, 21):  # 20 humans for performance test
                await system.add_human(f"human_perf_{i:03d}")
            
            # Run distribution
            await system.resource_pool.distribute_weekly()
            end_time = time.time()
            
            duration = end_time - start_time
            
            # Performance validation (should complete in reasonable time)
            assert duration < 10.0  # Should complete in less than 10 seconds
            
            self.record_test_result(test_name, True, f"Performance test passed (Duration: {duration:.2f}s)")
            
        except Exception as e:
            self.record_test_result(test_name, False, f"Error: {str(e)}")
    
    def record_test_result(self, test_name, passed, message):
        """Record test result"""
        if passed:
            self.tests_passed += 1
            status = "✅ PASSED"
            style = "green"
        else:
            self.tests_failed += 1
            status = "❌ FAILED"
            style = "red"
        
        self.results.append({
            'test': test_name,
            'status': status,
            'message': message,
            'style': style
        })
        
        self.console.print(f"{status} {test_name}: {message}", style=style)
    
    def display_results(self):
        """Display comprehensive test results"""
        
        # Summary panel
        total_tests = self.tests_passed + self.tests_failed
        success_rate = (self.tests_passed / total_tests * 100) if total_tests > 0 else 0
        
        summary = f"""
🧪 Total Tests: {total_tests}
✅ Passed: {self.tests_passed}
❌ Failed: {self.tests_failed}
📊 Success Rate: {success_rate:.1f}%
        """
        
        self.console.print(Panel(summary, title="Test Summary", style="bold blue"))
        
        # Results table
        table = Table(title="Detailed Test Results")
        table.add_column("Test", style="cyan")
        table.add_column("Status", style="white")
        table.add_column("Message", style="white")
        
        for result in self.results:
            table.add_row(
                result['test'],
                result['status'],
                result['message']
            )
        
        self.console.print(table)
        
        # Final status
        if self.tests_failed == 0:
            self.console.print(Panel("🎉 ALL TESTS PASSED! Liberation System is ready.", style="bold green"))
        else:
            self.console.print(Panel(f"⚠️  {self.tests_failed} tests failed. Check logs for details.", style="bold red"))

async def main():
    """Run integration tests"""
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('data/integration_test.log'),
            logging.StreamHandler()
        ]
    )
    
    # Run tests
    test_runner = IntegrationTest()
    await test_runner.run_all_tests()
    
    # Return appropriate exit code
    sys.exit(0 if test_runner.tests_failed == 0 else 1)

if __name__ == "__main__":
    asyncio.run(main())
