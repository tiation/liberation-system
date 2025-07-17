import asyncio
import logging
from Adaptive_Strategies import AdaptiveCapacityManager, AdaptiveConfiguration, AdaptiveStrategy
from Mesh_Network.Advanced_Node_Discovery import AdvancedMeshNode, NetworkMetrics, GeoLocation

# Configure logging
logging.basicConfig(level=logging.INFO)

# Create adaptive capacity manager with hybrid strategy
config = AdaptiveConfiguration(strategy=AdaptiveStrategy.HYBRID)
capacity_manager = AdaptiveCapacityManager(config)

async def monitor_and_adjust(node: AdvancedMeshNode):
    while True:
        try:
            # Step 1: Collect Historical Data
            await capacity_manager.collect_performance_data(node)

            # Step 2-4: Detect Patterns, Predict, and Adjust
            adjustments = await capacity_manager.analyze_and_adjust_capacity(node)
            print(f"Adjusted capacities for {node.id}: {adjustments}")

            # Monitor every hour
            await asyncio.sleep(3600)
        
        except Exception as e:
            logging.error(f"Error during monitoring: {e}")
            await asyncio.sleep(3600)  # Wait before retrying

# Example node creation
test_node = AdvancedMeshNode(
    id="adaptive_test_node",
    host="127.0.0.1",
    port=8000,
    location=GeoLocation(37.7749, -122.4194, "United States", "San Francisco", "CA"),
    metrics=NetworkMetrics(cpu_usage=60.0, memory_usage=45.0, network_load=70.0, uptime=99.5)
)

# Start the monitoring loop
asyncio.run(monitor_and_adjust(test_node))

