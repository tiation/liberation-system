# Add error handling and logging
import logging
from typing import Tuple

class MeshNode:
    def __init__(self, id: str):
        self.id = id
        self.connections = set()
        self.data_store = {}
        self.transmission_power = 1.0
        self.status = "active"
        self.last_seen = 0.0  # timestamp

    def is_healthy(self) -> bool:
        """Check if node is functioning properly"""
        return self.status == "active" and self.transmission_power > 0.5

class ResilientMesh:
    def __init__(self):
        self.nodes: Dict[str, MeshNode] = {}
        self.routes: Dict[str, List[str]] = {}
        self.active_transfers = set()
        self.logger = logging.getLogger(__name__)

    async def _discover_nodes(self):
        try:
            for i in range(random.randint(1, 5)):
                node_id = f"node_{len(self.nodes)}"
                new_node = MeshNode(node_id)
                self.nodes[node_id] = new_node
                self.logger.info(f"Discovered new node: {node_id}")
        except Exception as e:
            self.logger.error(f"Node discovery failed: {e}")

    async def _optimize_connections(self):
        try:
            for node in self.nodes.values():
                if not node.is_healthy():
                    continue
                nearby = self._find_nearby_nodes(node.id)
                optimal = self._calculate_optimal_connections(nearby)
                node.connections.update(optimal)
        except Exception as e:
            self.logger.error(f"Connection optimization failed: {e}")

class NeuralMesh:
    def __init__(self):
        self.mesh = ResilientMesh()
        self.patterns = {}
        self.learning_rate = 0.01
        self.performance_history = []

    async def _observe_patterns(self):
        """Enhanced pattern observation"""
        current_performance = await self._measure_network_performance()
        self.performance_history.append(current_performance)
        
        if len(self.performance_history) > 100:
            self.performance_history = self.performance_history[-100:]

    async def _measure_network_performance(self) -> float:
        """Measure overall network performance"""
        active_nodes = sum(1 for node in self.mesh.nodes.values() if node.is_healthy())
        total_nodes = len(self.mesh.nodes)
        return active_nodes / total_nodes if total_nodes > 0 else 0.0

class EnhancedMesh:
    def __init__(self):
        self.neural = NeuralMesh()
        self.features = {
            "self_repair": True,
            "load_balancing": True,
            "path_optimization": True,
            "knowledge_sharing": True
        }
        self.metrics = {
            "uptime": 0.0,
            "reliability": 0.0,
            "efficiency": 0.0
        }

    async def run_enhanced(self):
        """Enhanced run with metrics and monitoring"""
        try:
            await asyncio.gather(
                self._run_mesh(),
                self._run_learning(),
                self._run_optimization(),
                self._run_sharing(),
                self._monitor_health()
            )
        except Exception as e:
            logging.error(f"Enhanced mesh operation failed: {e}")

    async def _monitor_health(self):
        """New method to monitor system health"""
        while True:
            health_status = await self._check_system_health()
            if not health_status[0]:
                logging.warning(f"System health issue: {health_status[1]}")
            await asyncio.sleep(5)

    async def _check_system_health(self) -> Tuple[bool, str]:
        """Check overall system health"""
        if not self.neural.mesh.nodes:
            return False, "No nodes in network"
        return True, "System healthy"
