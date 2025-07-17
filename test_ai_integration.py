#!/usr/bin/env python3
"""
Interactive test for AI Load Balancer integration
"""

import asyncio
import logging
import time
import uuid
from core.ai_load_balancer import AILoadBalancer, LoadBalancingTask, NodeCapacity
from rich.console import Console
from rich.panel import Panel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

console = Console()

async def simulate_node_health_check():
    """Simulate a node health check"""
    import random
    return {
        'cpu_usage': random.uniform(10, 80),
        'memory_usage': random.uniform(20, 70),
        'response_time': random.uniform(50, 500),
        'error_rate': random.uniform(0, 2),
        'active_connections': random.randint(10, 100)
    }

async def test_ai_load_balancer():
    """Test AI Load Balancer functionality"""
    
    console.print(Panel.fit("🤖 AI Load Balancer Integration Test", style="bold cyan"))
    
    # Initialize AI load balancer
    console.print("🔄 Initializing AI Load Balancer...")
    ai_balancer = AILoadBalancer()
    
    try:
        await ai_balancer.initialize_ai_systems()
        console.print("✅ AI Load Balancer initialized successfully")
        
        # Register test nodes
        console.print("📝 Registering test nodes...")
        
        for i in range(3):
            node_id = f"test_node_{i+1}"
            node_capacity = NodeCapacity(
                node_id=node_id,
                max_connections=1000,
                max_cpu_usage=80.0,
                max_memory_usage=85.0,
                weight=1.0
            )
            
            await ai_balancer.register_node(node_id, node_capacity, simulate_node_health_check)
            console.print(f"✅ Registered node: {node_id}")
        
        # Submit test tasks
        console.print("🎯 Submitting test tasks...")
        
        tasks = []
        for i in range(10):
            task = LoadBalancingTask(
                task_id=str(uuid.uuid4()),
                task_type="mesh_communication",
                payload={"message": f"AI test message {i+1}"},
                priority=1
            )
            tasks.append(task)
            await ai_balancer.submit_task(task)
            console.print(f"📤 Submitted task {i+1}")
            
        # Wait for tasks to process
        console.print("⏳ Processing tasks...")
        await asyncio.sleep(5)
        
        # Display AI dashboard
        console.print("\n📊 AI Load Balancer Dashboard:")
        await ai_balancer.display_ai_dashboard()
        
        # Test AI-enhanced node selection
        console.print("\n🎯 Testing AI-enhanced node selection...")
        
        test_task = LoadBalancingTask(
            task_id=str(uuid.uuid4()),
            task_type="mesh_communication",
            payload={"message": "AI selection test"},
            priority=1
        )
        
        optimal_node = await ai_balancer.get_optimal_node_ai(test_task)
        console.print(f"🎯 AI selected optimal node: {optimal_node}")
        
        # Get comprehensive statistics
        stats = await ai_balancer.get_ai_statistics()
        console.print(f"\n📈 AI Statistics:")
        console.print(f"  - Predictions made: {stats['ai_statistics']['predictions_made']}")
        console.print(f"  - Scaling actions: {stats['ai_statistics']['scaling_actions']}")
        console.print(f"  - Auto discoveries: {stats['ai_statistics']['auto_discoveries']}")
        console.print(f"  - Traffic patterns: {stats['traffic_insights']['total_patterns']}")
        
        # Test predictive scaling simulation
        console.print("\n🔮 Testing predictive scaling...")
        
        # Simulate high load scenario
        for i in range(20):
            high_load_task = LoadBalancingTask(
                task_id=str(uuid.uuid4()),
                task_type="high_load_test",
                payload={"load_simulation": True},
                priority=2
            )
            await ai_balancer.submit_task(high_load_task)
        
        # Wait for prediction and scaling
        await asyncio.sleep(10)
        
        # Final dashboard display
        console.print("\n📊 Final AI Load Balancer Status:")
        await ai_balancer.display_ai_dashboard()
        
        console.print("\n✅ AI Load Balancer integration test completed successfully!")
        
    except Exception as e:
        console.print(f"❌ Test failed with error: {e}")
        logger.error(f"AI Load Balancer test failed: {e}")
        raise

async def main():
    """Main test function"""
    await test_ai_load_balancer()

if __name__ == "__main__":
    asyncio.run(main())
