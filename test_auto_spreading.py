#!/usr/bin/env python3
"""
Liberation System - Automatic Spreading Test
Tests the automatic mesh network spreading functionality
"""

import asyncio
import logging
import time
import sys
import os
import signal

sys.path.append(os.path.join(os.path.dirname(__file__), 'mesh', 'Mesh_Network'))
from mesh_network_clean import MeshNode, MessageType

# Configure logging with enhanced format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

class AutoSpreadingTest:
    """Test automatic spreading functionality"""
    
    def __init__(self):
        self.nodes = []
        self.logger = logging.getLogger("AutoSpreadingTest")
        self.running = True
        
    async def create_auto_spreading_nodes(self, count: int = 5):
        """Create nodes with automatic spreading enabled"""
        self.logger.info(f"🚀 Creating {count} auto-spreading nodes...")
        
        # Create nodes with different ports
        for i in range(count):
            node = MeshNode(
                id=f"auto_node_{i+1}",
                host="localhost",
                port=9000 + i,
                auto_spread=True
            )
            self.nodes.append(node)
            self.logger.info(f"Created node {node.id} on port {node.port}")
        
        return self.nodes
    
    async def start_spreading_network(self):
        """Start the automatic spreading network"""
        self.logger.info("🌐 Starting automatic spreading network...")
        
        # Start all nodes with auto-spreading
        tasks = []
        for node in self.nodes:
            task = asyncio.create_task(node.start_auto_spreading())
            tasks.append(task)
        
        # Give nodes time to discover each other
        await asyncio.sleep(10)
        
        # Log initial network state
        self.logger.info("📊 Initial network state:")
        for node in self.nodes:
            stats = node.get_network_stats()
            self.logger.info(f"  {node.id}: {stats['connections_active']} connections, "
                           f"{stats['messages_sent']} sent, {stats['messages_received']} received")
        
        return tasks
    
    async def monitor_spreading(self, duration: int = 180):
        """Monitor the spreading process"""
        self.logger.info(f"📡 Monitoring automatic spreading for {duration} seconds...")
        
        start_time = time.time()
        last_report = start_time
        
        while time.time() - start_time < duration and self.running:
            current_time = time.time()
            
            # Report every 30 seconds
            if current_time - last_report >= 30:
                self.logger.info("🔄 Network Status Update:")
                
                total_connections = 0
                total_messages_sent = 0
                total_messages_received = 0
                
                for node in self.nodes:
                    stats = node.get_network_stats()
                    total_connections += stats['connections_active']
                    total_messages_sent += stats['messages_sent']
                    total_messages_received += stats['messages_received']
                    
                    # Show some connection details
                    peer_count = len(node.connections)
                    active_peers = [pid for pid, conn in node.connections.items() 
                                  if conn['status'] == 'connected']
                    
                    self.logger.info(f"  {node.id}: {peer_count} peers, "
                                   f"{stats['messages_sent']} sent, "
                                   f"{stats['messages_received']} received")
                
                self.logger.info(f"📈 Network totals: {total_connections} connections, "
                               f"{total_messages_sent} messages sent, "
                               f"{total_messages_received} messages received")
                
                last_report = current_time
            
            await asyncio.sleep(1)
    
    async def demonstrate_truth_spreading(self):
        """Demonstrate automatic truth spreading"""
        self.logger.info("🌟 Demonstrating automatic truth spreading...")
        
        # Let the network run for a while to generate truth messages
        await asyncio.sleep(60)
        
        # Check for truth messages in node data stores
        truth_count = 0
        for node in self.nodes:
            for key, value in node.data_store.items():
                if "truth" in key.lower() or "liberation" in str(value).lower():
                    truth_count += 1
        
        self.logger.info(f"💡 {truth_count} truth messages found in network")
    
    async def demonstrate_resource_spreading(self):
        """Demonstrate automatic resource spreading"""
        self.logger.info("💰 Demonstrating automatic resource spreading...")
        
        # Count resource messages
        resource_count = 0
        for node in self.nodes:
            resource_count += node.network_stats.get('messages_sent', 0)
        
        self.logger.info(f"💸 {resource_count} resource messages distributed")
    
    async def cleanup_nodes(self):
        """Clean up all nodes"""
        self.logger.info("🧹 Cleaning up nodes...")
        
        for node in self.nodes:
            try:
                await node.stop_auto_spreading()
                await node.shutdown()
            except Exception as e:
                self.logger.error(f"Error cleaning up {node.id}: {e}")
        
        self.logger.info("✅ Cleanup complete")
    
    def signal_handler(self, signum, frame):
        """Handle interrupt signal"""
        self.logger.info("🛑 Received interrupt signal, stopping...")
        self.running = False
    
    async def run_demonstration(self):
        """Run the full automatic spreading demonstration"""
        self.logger.info("🎯 Starting Liberation System Automatic Spreading Demo")
        self.logger.info("=" * 70)
        
        # Set up signal handler
        signal.signal(signal.SIGINT, self.signal_handler)
        
        try:
            # Create auto-spreading nodes
            await self.create_auto_spreading_nodes(5)
            
            # Start the spreading network
            network_tasks = await self.start_spreading_network()
            
            # Monitor the spreading process
            await self.monitor_spreading(180)  # 3 minutes
            
            # Demonstrate specific features
            await self.demonstrate_truth_spreading()
            await self.demonstrate_resource_spreading()
            
            # Show final statistics
            self.logger.info("📊 Final Network Statistics:")
            for node in self.nodes:
                stats = node.get_network_stats()
                self.logger.info(f"  {node.id}: {stats}")
            
            # Calculate network efficiency
            total_sent = sum(node.network_stats['messages_sent'] for node in self.nodes)
            total_received = sum(node.network_stats['messages_received'] for node in self.nodes)
            efficiency = (total_received / total_sent * 100) if total_sent > 0 else 0
            
            self.logger.info(f"🎯 Network Efficiency: {efficiency:.1f}%")
            self.logger.info("🎉 Automatic spreading demonstration complete!")
            
        except Exception as e:
            self.logger.error(f"Demonstration failed: {e}")
            
        finally:
            # Clean up
            await self.cleanup_nodes()

async def main():
    """Main demonstration runner"""
    demo = AutoSpreadingTest()
    
    try:
        await demo.run_demonstration()
        return 0
    except KeyboardInterrupt:
        logging.info("Demo interrupted by user")
        return 1
    except Exception as e:
        logging.error(f"Demo failed: {e}")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))
