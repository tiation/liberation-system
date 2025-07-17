#!/usr/bin/env python3
"""
Node Optimization and Update Demo
Demonstrates geolocation updates, metrics collection, and connection optimization
for the Liberation System's mesh network with replication and sharding capabilities.
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import Dict, List, Any

# Import our advanced discovery system
from Mesh_Network.Advanced_Node_Discovery import (
    AdvancedNodeDiscovery,
    AdvancedMeshNode,
    NodeType,
    NetworkMetrics,
    GeoLocation
)

# Import dynamic load balancer
from Dynamic_Load_Balancer import LoadBalancer

class ReplicationShardingMonitor:
    """Monitor and manage replication and sharding characteristics"""
    
    def __init__(self, discovery_service: AdvancedNodeDiscovery):
        self.discovery = discovery_service
        self.replication_factor = 3  # Default replication factor
        self.shard_count = 5  # Default number of shards
        self.logger = logging.getLogger(__name__)
        self.replication_status = {}
        self.shard_assignments = {}
        
    async def monitor_replication_health(self) -> Dict[str, Any]:
        """Monitor the health of data replication across nodes"""
        replication_health = {
            "total_nodes": len(self.discovery.discovered_nodes),
            "active_replicas": 0,
            "failed_replicas": 0,
            "replication_factor": self.replication_factor,
            "health_score": 0.0,
            "timestamp": datetime.now().isoformat()
        }
        
        active_nodes = [
            node for node in self.discovery.discovered_nodes.values()
            if node.status == "active" and time.time() - node.last_seen < 300
        ]
        
        replication_health["active_replicas"] = len(active_nodes)
        replication_health["failed_replicas"] = replication_health["total_nodes"] - len(active_nodes)
        
        # Calculate health score based on available replicas
        if self.replication_factor > 0:
            replication_health["health_score"] = min(1.0, len(active_nodes) / self.replication_factor)
        
        self.logger.info(f"Replication health: {replication_health['health_score']:.2f} "
                        f"({len(active_nodes)}/{self.replication_factor} replicas active)")
        
        return replication_health
    
    async def monitor_shard_distribution(self) -> Dict[str, Any]:
        """Monitor the distribution of shards across nodes"""
        shard_distribution = {
            "total_shards": self.shard_count,
            "assigned_shards": 0,
            "unassigned_shards": 0,
            "shard_balance": 0.0,
            "shard_assignments": {},
            "timestamp": datetime.now().isoformat()
        }
        
        # Group nodes by region for better shard distribution
        nodes_by_region = {}
        for node in self.discovery.discovered_nodes.values():
            if node.status == "active":
                region_key = f"{node.location.country}:{node.location.region}"
                if region_key not in nodes_by_region:
                    nodes_by_region[region_key] = []
                nodes_by_region[region_key].append(node)
        
        # Assign shards based on node capacity and geographical distribution
        assigned_shards = 0
        for shard_id in range(self.shard_count):
            # Find the best region for this shard
            best_region = None
            best_score = -1
            
            for region, nodes in nodes_by_region.items():
                if not nodes:
                    continue
                    
                # Calculate region score based on node quality and capacity
                region_score = sum(node.metrics.calculate_quality_score() for node in nodes) / len(nodes)
                if region_score > best_score:
                    best_score = region_score
                    best_region = region
            
            if best_region and nodes_by_region[best_region]:
                # Assign shard to best node in the region
                best_node = max(nodes_by_region[best_region], 
                              key=lambda n: n.metrics.calculate_quality_score())
                shard_distribution["shard_assignments"][f"shard_{shard_id}"] = {
                    "node_id": best_node.id,
                    "region": best_region,
                    "quality_score": best_node.metrics.calculate_quality_score()
                }
                assigned_shards += 1
        
        shard_distribution["assigned_shards"] = assigned_shards
        shard_distribution["unassigned_shards"] = self.shard_count - assigned_shards
        
        if self.shard_count > 0:
            shard_distribution["shard_balance"] = assigned_shards / self.shard_count
        
        self.logger.info(f"Shard distribution: {shard_distribution['shard_balance']:.2f} "
                        f"({assigned_shards}/{self.shard_count} shards assigned)")
        
        return shard_distribution
    
    async def optimize_for_replication_sharding(self, local_node: AdvancedMeshNode) -> Dict[str, Any]:
        """Optimize node connections for better replication and sharding"""
        optimization_results = {
            "timestamp": datetime.now().isoformat(),
            "optimizations_applied": [],
            "performance_improvements": {}
        }
        
        # Get current topology
        topology = self.discovery.get_network_topology()
        
        # Optimize for replication
        replication_health = await self.monitor_replication_health()
        if replication_health["health_score"] < 0.8:  # Below 80% health
            # Find nodes in different regions for better fault tolerance
            candidates = list(self.discovery.discovered_nodes.values())
            diverse_candidates = await self.discovery._optimize_node_selection(local_node, candidates)
            
            # Update connections to prioritize geographical diversity
            if diverse_candidates:
                optimization_results["optimizations_applied"].append("geographical_diversity")
                local_node.connections.update({
                    node.id: {
                        "host": node.host,
                        "port": node.port,
                        "role": "replication_peer",
                        "quality_score": node.metrics.calculate_quality_score()
                    } for node in diverse_candidates[:self.replication_factor]
                })
        
        # Optimize for sharding
        shard_distribution = await self.monitor_shard_distribution()
        if shard_distribution["shard_balance"] < 0.9:  # Below 90% shard assignment
            # Prioritize high-capacity nodes for shard hosting
            high_capacity_nodes = [
                node for node in self.discovery.discovered_nodes.values()
                if node.capabilities.storage_capacity > 500 and 
                   node.metrics.calculate_quality_score() > 0.7
            ]
            
            if high_capacity_nodes:
                optimization_results["optimizations_applied"].append("shard_optimization")
                for node in high_capacity_nodes[:3]:  # Top 3 nodes
                    local_node.connections[node.id] = {
                        "host": node.host,
                        "port": node.port,
                        "role": "shard_host",
                        "storage_capacity": node.capabilities.storage_capacity,
                        "quality_score": node.metrics.calculate_quality_score()
                    }
        
        # Calculate performance improvements
        new_topology = self.discovery.get_network_topology()
        optimization_results["performance_improvements"] = {
            "network_health_change": new_topology["network_health"] - topology["network_health"],
            "average_latency_change": topology["average_latency"] - new_topology["average_latency"],
            "total_connections": len(local_node.connections)
        }
        
        return optimization_results

class NodeOptimizationDemo:
    """Demonstration of node optimization with replication and sharding monitoring"""
    
    def __init__(self):
        self.discovery = AdvancedNodeDiscovery()
        self.monitor = ReplicationShardingMonitor(self.discovery)
        self.load_balancer = LoadBalancer(self.discovery)
        self.logger = logging.getLogger(__name__)
        
    async def run_optimization_demo(self):
        """Run the complete optimization demonstration"""
        print("🚀 Starting Node Optimization and Update Demo")
        print("=" * 60)
        
        # Create a local node
        local_node = AdvancedMeshNode(
            id="optimization_demo_node",
            host="127.0.0.1",
            port=8000,
            node_type=NodeType.GATEWAY
        )
        
        # Phase 1: Initial Discovery
        print("\n📡 Phase 1: Initial Node Discovery")
        print("-" * 40)
        discovered_nodes = await self.discovery.discover_nodes(local_node)
        print(f"✅ Discovered {len(discovered_nodes)} nodes")
        
        # Phase 2: Geolocation and Metrics Updates
        print("\n🌍 Phase 2: Geolocation and Metrics Updates")
        print("-" * 40)
        
        # Update geolocation for all nodes
        for node in discovered_nodes:
            if not node.location or (node.location.latitude == 0 and node.location.longitude == 0):
                print(f"🔄 Updating location for {node.id}")
                node.location = await self.discovery.geolocation_service.get_local_location()
                if not node.location:
                    node.location = GeoLocation(
                        latitude=40.7128 + (hash(node.id) % 100) / 100,
                        longitude=-74.0060 + (hash(node.id) % 100) / 100,
                        city="Simulated City",
                        country="Simulated Country"
                    )
        
        # Update metrics for all nodes
        print("📊 Updating network metrics...")
        for node in discovered_nodes:
            await self.discovery.update_node_metrics(node.id)
        
        # Phase 3: Connection Optimization
        print("\n⚡ Phase 3: Connection Optimization")
        print("-" * 40)
        
        # Run optimization
        optimized_nodes = await self.discovery._optimize_node_selection(local_node, discovered_nodes)
        print(f"✅ Optimized connections: {len(optimized_nodes)} nodes selected")
        
        # Display optimization results
        for i, node in enumerate(optimized_nodes, 1):
            score = await self.discovery._calculate_node_score(local_node, node)
            print(f"  {i}. {node.id} - Score: {score:.3f}, "
                  f"Latency: {node.metrics.latency:.2f}ms, "
                  f"Quality: {node.metrics.calculate_quality_score():.3f}")
        
        # Phase 4: Replication and Sharding Monitoring
        print("\n🔄 Phase 4: Replication and Sharding Monitoring")
        print("-" * 40)
        
        # Monitor replication health
        replication_health = await self.monitor.monitor_replication_health()
        print(f"📊 Replication Health: {replication_health['health_score']:.2f}")
        print(f"   Active Replicas: {replication_health['active_replicas']}")
        print(f"   Failed Replicas: {replication_health['failed_replicas']}")
        
        # Monitor shard distribution
        shard_distribution = await self.monitor.monitor_shard_distribution()
        print(f"🗂️  Shard Distribution: {shard_distribution['shard_balance']:.2f}")
        print(f"   Assigned Shards: {shard_distribution['assigned_shards']}")
        print(f"   Unassigned Shards: {shard_distribution['unassigned_shards']}")
        
        # Phase 5: Optimization for Replication and Sharding
        print("\n⚙️  Phase 5: Optimization for Replication and Sharding")
        print("-" * 40)
        
        optimization_results = await self.monitor.optimize_for_replication_sharding(local_node)
        print(f"🔧 Optimizations Applied: {optimization_results['optimizations_applied']}")
        
        if optimization_results['performance_improvements']:
            improvements = optimization_results['performance_improvements']
            print(f"📈 Performance Improvements:")
            print(f"   Network Health Change: {improvements['network_health_change']:+.3f}")
            print(f"   Average Latency Change: {improvements['average_latency_change']:+.2f}ms")
            print(f"   Total Connections: {improvements['total_connections']}")
        
        # Phase 6: Load Balancing
        print("\n⚖️  Phase 6: Dynamic Load Balancing")
        print("-" * 40)
        
        # Simulate load balancing
        await self.load_balancer.distribute_load(discovered_nodes)
        
        # Phase 7: Network Topology Analysis
        print("\n🕸️  Phase 7: Network Topology Analysis")
        print("-" * 40)
        
        topology = self.discovery.get_network_topology()
        print(f"📊 Network Topology Summary:")
        print(f"   Total Nodes: {topology['total_nodes']}")
        print(f"   Average Latency: {topology['average_latency']:.2f}ms")
        print(f"   Network Health: {topology['network_health']:.3f}")
        print(f"   Regions: {len(topology['nodes_by_region'])}")
        
        # Display regional distribution
        for region, nodes in topology['nodes_by_region'].items():
            print(f"   {region}: {len(nodes)} nodes")
        
        print("\n🎯 Node Optimization Demo Complete!")
        print("=" * 60)
        
        return {
            "discovered_nodes": len(discovered_nodes),
            "optimized_nodes": len(optimized_nodes),
            "replication_health": replication_health,
            "shard_distribution": shard_distribution,
            "optimization_results": optimization_results,
            "network_topology": topology
        }
    
    async def run_continuous_optimization(self, local_node: AdvancedMeshNode, duration_minutes: int = 30):
        """Run continuous optimization for a specified duration"""
        print(f"🔄 Starting continuous optimization for {duration_minutes} minutes...")
        
        end_time = time.time() + (duration_minutes * 60)
        
        # Start background tasks
        tasks = [
            asyncio.create_task(self.discovery.start_periodic_updates()),
            asyncio.create_task(self.discovery.start_connection_optimization(local_node))
        ]
        
        try:
            # Run optimization monitoring
            while time.time() < end_time:
                await asyncio.sleep(60)  # Check every minute
                
                # Monitor and report status
                replication_health = await self.monitor.monitor_replication_health()
                shard_distribution = await self.monitor.monitor_shard_distribution()
                
                print(f"⏰ Status Update - "
                      f"Replication: {replication_health['health_score']:.2f}, "
                      f"Sharding: {shard_distribution['shard_balance']:.2f}")
                
        except KeyboardInterrupt:
            print("\n🛑 Optimization stopped by user")
        finally:
            # Cancel background tasks
            for task in tasks:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            
            print("✅ Continuous optimization completed")

async def main():
    """Main demonstration function"""
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run the demonstration
    demo = NodeOptimizationDemo()
    
    try:
        # Run basic optimization demo
        results = await demo.run_optimization_demo()
        
        # Optionally run continuous optimization
        print("\n🔄 Would you like to run continuous optimization? (Press Ctrl+C to stop)")
        input("Press Enter to continue or Ctrl+C to exit...")
        
        local_node = AdvancedMeshNode(
            id="continuous_optimization_node",
            host="127.0.0.1",
            port=8001,
            node_type=NodeType.GATEWAY
        )
        
        await demo.run_continuous_optimization(local_node, duration_minutes=5)
        
    except KeyboardInterrupt:
        print("\n👋 Demo stopped by user")
    except Exception as e:
        print(f"❌ Error during demo: {e}")
        logging.error(f"Demo error: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(main())
