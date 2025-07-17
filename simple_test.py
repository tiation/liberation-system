#!/usr/bin/env python3
"""
Simple Liberation System Test
Demonstrates all components working together
"""

import asyncio
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_resource_system():
    """Test resource distribution"""
    print("🔄 Testing Resource Distribution System...")
    
    # Import and test
    from core.resource_distribution import SystemCore
    system = SystemCore()
    await system.initialize()
    
    # Add test humans
    for i in range(1, 4):
        await system.add_human(f"human_{i:06d}")
    
    # Run distribution
    await system.resource_pool.distribute_weekly()
    
    # Get stats
    stats = await system.get_system_stats()
    print(f"✅ Resource system: {stats['total_humans']} humans, ${stats['total_distributed']:,.2f} distributed")
    
    return True

async def test_automation_system():
    """Test automation system"""
    print("🔄 Testing Automation System...")
    
    # Import and test
    import importlib.util
    spec = importlib.util.spec_from_file_location("automation_system", "core/automation-system.py")
    automation_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(automation_module)
    SystemManager = automation_module.SystemManager
    manager = SystemManager()
    await manager.initialize()
    await manager.setup_all_systems()
    
    # Run one cycle of tasks
    for task in manager.automation.tasks.values():
        await manager.automation._run_task(task)
    
    # Get stats
    stats = await manager.automation.get_task_statistics()
    print(f"✅ Automation system: {stats['total_tasks']} tasks, {stats['success_rate']:.1f}% success rate")
    
    return True

async def test_security_system():
    """Test security system"""
    print("🔄 Testing Security System...")
    
    # Import and test
    from security.trust_default import AntiSecurity
    security = AntiSecurity()
    
    # Test valid request
    valid_request = {
        "human_id": "human_000001",
        "resource_id": "resource_test",
        "action": "access"
    }
    
    response = security.process_request(valid_request)
    print(f"✅ Security system: Access granted = {response['access']}")
    
    return True

async def main():
    """Run all tests"""
    print("🌟 Liberation System - Simple Integration Test")
    print("=" * 50)
    
    try:
        # Test all systems
        await test_resource_system()
        await test_automation_system()
        await test_security_system()
        
        print("\n🎉 ALL TESTS PASSED!")
        print("📊 Liberation System is fully operational!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
