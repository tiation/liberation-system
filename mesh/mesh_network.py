#!/usr/bin/env python3
"""
Main entry point for Liberation System Mesh Network
Integrates all components: sharding, monitoring, discovery, and AI capabilities
"""

import asyncio
import logging
import os
import signal
import sys
from typing import Dict, Any

from Mesh_Network.Sharding_Strategy import ShardingStrategy
from Mesh_Network.Advanced_Node_Discovery import (
    AdvancedNodeDiscovery,
    AdvancedMeshNode,
    GeoLocation,
    NetworkMetrics,
    NodeCapabilities,
    NodeType
)
from Mesh_Network.Monitoring_System import MonitoringSystem
from Mesh_Network.Performance_Optimization import MeshNetworkOptimizer
from Mesh_Network.Knowledge_Sharing_AI import AICapabilities

# Configuration from environment variables
CONFIG = {
    "TOTAL_SHARDS": int(os.getenv("TOTAL_SHARDS", "256")),
    "REPLICATION_FACTOR": int(os.getenv("REPLICATION_FACTOR", "3")),
    "DASHBOARD_HOST": os.getenv("DASHBOARD_HOST", "localhost"),
    "DASHBOARD_PORT": int(os.getenv("DASHBOARD_PORT", "8080")),
    "LOG_LEVEL": os.getenv("LOG_LEVEL", "INFO"),
    "MONITORING_ENABLED": os.getenv("MONITORING_ENABLED", "true").lower() == "true",
    "CACHE_TTL": int(os.getenv("CACHE_TTL", "60"))
}

# Configure logging with dark neon theme
logging.basicConfig(
    level=getattr(logging, CONFIG["LOG_LEVEL"]),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('mesh_network.log')
    ]
)

class MeshNetworkApplication:
    """Main application class for the mesh network system"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.running = False
        
        # Initialize core components
        self.sharding_strategy = ShardingStrategy(
            total_shards=CONFIG["TOTAL_SHARDS"],
            replication_factor=CONFIG["REPLICATION_FACTOR"]
        )
        
        self.node_discovery = AdvancedNodeDiscovery()
        self.optimizer = MeshNetworkOptimizer(self.sharding_strategy, self.node_discovery)
        self.ai_capabilities = AICapabilities(self.sharding_strategy)
        
        # Initialize monitoring system if enabled
        if CONFIG["MONITORING_ENABLED"]:
            self.monitoring_system = MonitoringSystem(self.sharding_strategy)
        else:
            self.monitoring_system = None
        
        # Setup signal handlers for graceful shutdown
        self._setup_signal_handlers()
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            self.logger.info(f"Received signal {signum}, initiating shutdown...")
            self.stop()
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def start(self):
        """Start the mesh network application"""
        self.running = True
        self.logger.info("🚀 Starting Liberation System Mesh Network...")
        
        try:
            # Initialize with some sample nodes for demonstration
            await self._initialize_sample_nodes()
            
            # Start monitoring system if enabled
            if self.monitoring_system:
                self.logger.info("📊 Starting monitoring system...")
                monitoring_task = asyncio.create_task(self.monitoring_system.start())
            
            # Start main application loop
            await self._run_application_loop()
            
        except Exception as e:
            self.logger.error(f"❌ Failed to start application: {e}")
            raise
    
    async def _initialize_sample_nodes(self):
        """Initialize sample nodes for demonstration"""
        self.logger.info("🔧 Initializing sample nodes...")
        
        sample_nodes = [
            AdvancedMeshNode(
                id="gateway_us_east",
                host="127.0.0.1",
                port=8000,
                node_type=NodeType.GATEWAY,
                location=GeoLocation(40.7128, -74.0060, "United States", "New York", "NY"),
                metrics=NetworkMetrics(latency=25.0, bandwidth=1000.0, uptime=99.9),
                capabilities=NodeCapabilities(max_connections=200, storage_capacity=10000, processing_power=4.0)
            ),
            AdvancedMeshNode(
                id="storage_us_west",
                host="127.0.0.1",
                port=8001,
                node_type=NodeType.STORAGE,
                location=GeoLocation(37.7749, -122.4194, "United States", "San Francisco", "CA"),
                metrics=NetworkMetrics(latency=30.0, bandwidth=800.0, uptime=99.8),
                capabilities=NodeCapabilities(max_connections=150, storage_capacity=50000, processing_power=2.5)
            ),
            AdvancedMeshNode(
                id="compute_eu_london",
                host="127.0.0.1",
                port=8002,
                node_type=NodeType.COMPUTE,
                location=GeoLocation(51.5074, -0.1278, "United Kingdom", "London", "England"),
                metrics=NetworkMetrics(latency=80.0, bandwidth=600.0, uptime=99.5),
                capabilities=NodeCapabilities(max_connections=100, storage_capacity=5000, processing_power=8.0)
            )
        ]
        
        # Add nodes to both discovery and sharding systems
        for node in sample_nodes:
            self.node_discovery.discovered_nodes[node.id] = node
            await self.sharding_strategy.add_node_to_shard(node)
        
        self.logger.info(f"✅ Initialized {len(sample_nodes)} sample nodes")
    
    async def _run_application_loop(self):
        """Main application loop"""
        self.logger.info("🔄 Starting main application loop...")
        
        while self.running:
            try:
                # Periodic tasks
                await self._perform_periodic_tasks()
                
                # Sleep for a bit before next iteration
                await asyncio.sleep(30)
                
            except Exception as e:
                self.logger.error(f"❌ Error in application loop: {e}")
                await asyncio.sleep(5)
    
    async def _perform_periodic_tasks(self):
        """Perform periodic maintenance tasks"""
        try:
            # Rebalance shards
            await self.sharding_strategy.rebalance_shards()
            
            # Get AI recommendations
            recommendations = self.ai_capabilities.recommend_node_scaling()
            if recommendations["recommendations"]:
                self.logger.info(f"🤖 AI Recommendations: {recommendations}")
            
            # Log system status
            if self.monitoring_system:
                status = self.monitoring_system.get_system_status()
                self.logger.info(f"📊 System Status: {status}")
            
        except Exception as e:
            self.logger.error(f"❌ Error in periodic tasks: {e}")
    
    def stop(self):
        """Stop the mesh network application"""
        self.logger.info("🛑 Stopping Liberation System Mesh Network...")
        self.running = False
        
        if self.monitoring_system:
            self.monitoring_system.stop()
        
        self.logger.info("✅ Application stopped successfully")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current application status"""
        status = {
            "running": self.running,
            "config": CONFIG,
            "nodes": len(self.sharding_strategy.nodes),
            "shards": len(self.sharding_strategy.shards)
        }
        
        if self.monitoring_system:
            status.update(self.monitoring_system.get_system_status())
        
        return status

async def main():
    """Main entry point"""
    app = MeshNetworkApplication()
    
    try:
        await app.start()
    except KeyboardInterrupt:
        app.logger.info("💡 Application interrupted by user")
    except Exception as e:
        app.logger.error(f"💥 Application failed: {e}")
        sys.exit(1)
    finally:
        app.stop()

if __name__ == "__main__":
    # Print startup banner
    banner = """
🌐 LIBERATION SYSTEM MESH NETWORK
==================================
🔗 Advanced P2P Mesh Network with AI
📊 Real-time Monitoring & Analytics
🚀 Enterprise-Grade Scalability
💎 Dark Neon Theme Interface
==================================
"""
    print(banner)
    
    # Run the application
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
