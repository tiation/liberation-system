#!/usr/bin/env python3

import asyncio
import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.abspath('.'))

# Create necessary directories
Path('logs').mkdir(exist_ok=True)
Path('data').mkdir(exist_ok=True)
Path('config').mkdir(exist_ok=True)

# Import and test core components
try:
    from core.resource_distribution import SystemCore as ResourceSystem
    print("✅ Resource distribution system imported successfully")
    
    from transformation.truth_spreader import TruthSystem
    print("✅ Truth spreading system imported successfully")
    
    from security.trust_default import AntiSecurity
    print("✅ Security system imported successfully")
    
    # Try to import mesh network - may not be available
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("mesh_network", "mesh/Mesh_Network/Mesh-Network.py")
        mesh_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mesh_module)
        EnhancedMesh = mesh_module.EnhancedMesh
        print("✅ Mesh network system imported successfully")
        mesh_available = True
    except Exception as e:
        print(f"⚠️  Mesh network not available - skipping: {e}")
        mesh_available = False
    
    from core.config import get_config
    print("✅ Configuration system imported successfully")
    
    print("\n🌟 All core components imported successfully!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

async def test_core_functionality():
    """Test core functionality"""
    print("\n🚀 Testing core functionality...")
    
    try:
        # Test resource system
        print("\n📊 Testing Resource Distribution System...")
        resource_system = ResourceSystem()
        await resource_system.initialize()
        
        # Add a test human
        await resource_system.add_human("test_human_001")
        
        # Test truth system
        print("\n📡 Testing Truth Spreading System...")
        truth_system = TruthSystem()
        await truth_system.initialize()
        
        # Add a test truth message
        await truth_system.spreader.add_truth_message(
            "Test message: Liberation system is working!",
            "test_system",
            priority=1
        )
        
        # Test security system
        print("\n🔒 Testing Security System...")
        security_system = AntiSecurity()
        test_request = {"action": "test", "user": "test_human_001"}
        result = security_system.process_request(test_request)
        print(f"Security result: {result}")
        
        # Test mesh network
        if mesh_available:
            print("\n🌐 Testing Mesh Network...")
            mesh_system = EnhancedMesh()
            # Add some test nodes
            await mesh_system.neural.mesh._discover_nodes()
            print(f"Mesh nodes: {len(mesh_system.neural.mesh.nodes)}")
        else:
            print("\n⚠️  Skipping mesh network test - not available")
        
        print("\n✅ All core systems tested successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🌟 LIBERATION SYSTEM CORE TEST 🌟")
    print("=" * 50)
    
    # Run the test
    success = asyncio.run(test_core_functionality())
    
    if success:
        print("\n🎉 Liberation System Core is ready!")
        print("Run 'python3 core/liberation_core.py' to start the full system.")
    else:
        print("\n❌ Core test failed. Check the errors above.")
        sys.exit(1)
