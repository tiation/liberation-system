import unittest
from unittest.mock import AsyncMock, patch
from core.ai_load_balancer import AILoadBalancer, LoadBalancingTask, NodeCapacity
import asyncio


class TestAILoadBalancer(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.get_event_loop()
        self.load_balancer = AILoadBalancer()
        
    async def asyncSetUp(self):
        await self.load_balancer.initialize_ai_systems()

    async def test_ai_scaled_up_node(self):
        # Setup test node capacity
        node_id = "test_node"
        capacity = NodeCapacity(node_id=node_id)
        health_check = AsyncMock(return_value={
            'cpu_usage': 10.0,
            'memory_usage': 20.0,
            'response_time': 100.0,
            'error_rate': 0.0
        })
        await self.load_balancer.register_node(node_id, capacity, health_check)

        # Submit task
        task = LoadBalancingTask(task_id="task-1", task_type="test_type", payload={})
        await self.load_balancer.submit_task(task)

        # Simulate system load
        with patch.object(self.load_balancer.predictor, 'predict_future_load', 
                          return_value=AsyncMock(predicted_load=0.8, urgency=10)):
            # Trigger predictive scaling
            await self.load_balancer._predictive_scaling_loop()

        # Check scaling action
        new_nodes = len(self.load_balancer.nodes) - 1  # Original node + scaled nodes
        self.assertGreater(new_nodes, 0, "Scaling up did not create any nodes")

    def tearDown(self):
        self.loop.close()


if __name__ == '__main__':
    unittest.main()
