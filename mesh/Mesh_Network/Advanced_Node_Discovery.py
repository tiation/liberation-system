#!/usr/bin/env python3
"""
Advanced Node Discovery for Liberation System Mesh Network
Implements geolocation and network metrics for optimized node placement
"""

import logging
import asyncio
import time
import json
import math
import random
import socket
import uuid
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

try:
    import aiohttp
    import psutil
except ImportError:
    print("Installing required dependencies...")
    import subprocess
    subprocess.check_call(["pip", "install", "aiohttp", "psutil"])
    import aiohttp
    import psutil

@dataclass
class GeoLocation:
    """Geographical location data for nodes"""
    latitude: float
    longitude: float
    country: str = ""
    city: str = ""
    region: str = ""
    timezone: str = ""
    isp: str = ""
    
    def distance_to(self, other: 'GeoLocation') -> float:
        """Calculate distance between two locations in kilometers using Haversine formula"""
        R = 6371  # Earth's radius in kilometers
        
        lat1, lon1 = math.radians(self.latitude), math.radians(self.longitude)
        lat2, lon2 = math.radians(other.latitude), math.radians(other.longitude)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c

@dataclass
class NetworkMetrics:
    """Network performance metrics for nodes"""
    latency: float = 0.0  # milliseconds
    bandwidth: float = 0.0  # Mbps
    packet_loss: float = 0.0  # percentage
    jitter: float = 0.0  # milliseconds
    uptime: float = 0.0  # percentage
    cpu_usage: float = 0.0  # percentage
    memory_usage: float = 0.0  # percentage
    network_load: float = 0.0  # percentage
    last_updated: datetime = field(default_factory=datetime.now)
    
    def calculate_quality_score(self) -> float:
        """Calculate overall network quality score (0-1)"""
        # Weighted quality calculation
        latency_score = max(0, 1 - (self.latency / 1000))  # Lower latency is better
        bandwidth_score = min(1, self.bandwidth / 100)  # Higher bandwidth is better
        loss_score = max(0, 1 - (self.packet_loss / 100))  # Lower packet loss is better
        uptime_score = self.uptime / 100  # Higher uptime is better
        
        # Weighted average
        quality = (latency_score * 0.3 + bandwidth_score * 0.25 + 
                  loss_score * 0.25 + uptime_score * 0.2)
        
        return min(1.0, max(0.0, quality))

@dataclass
class NodeCapabilities:
    """Node capabilities and resource information"""
    max_connections: int = 50
    storage_capacity: int = 1000  # MB
    processing_power: float = 1.0  # relative scale
    supported_protocols: List[str] = field(default_factory=lambda: ['tcp', 'udp', 'websocket'])
    trust_level: float = 1.0  # 0-1 scale (trust-first principle)
    specializations: List[str] = field(default_factory=list)  # e.g., ['relay', 'storage', 'compute']
    
class NodeType(Enum):
    """Types of nodes in the mesh network"""
    STANDARD = "standard"
    RELAY = "relay"
    STORAGE = "storage"
    COMPUTE = "compute"
    GATEWAY = "gateway"
    BOOTSTRAP = "bootstrap"

@dataclass
class AdvancedMeshNode:
    """Advanced mesh node with geolocation and network metrics"""
    id: str
    host: str
    port: int
    node_type: NodeType = NodeType.STANDARD
    location: Optional[GeoLocation] = None
    metrics: NetworkMetrics = field(default_factory=NetworkMetrics)
    capabilities: NodeCapabilities = field(default_factory=NodeCapabilities)
    connections: Dict[str, Dict] = field(default_factory=dict)
    last_seen: float = field(default_factory=time.time)
    status: str = "active"
    trust_score: float = 1.0  # Trust-first principle
    
    def __post_init__(self):
        if self.location is None:
            self.location = GeoLocation(0.0, 0.0)

class GeolocationService:
    """Service to fetch geolocation data"""
    
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 3600  # 1 hour
        self.logger = logging.getLogger(__name__)
        
    async def get_location_by_ip(self, ip_address: str) -> Optional[GeoLocation]:
        """Get geolocation data for an IP address"""
        # Check cache first
        if ip_address in self.cache:
            cached_data, timestamp = self.cache[ip_address]
            if time.time() - timestamp < self.cache_ttl:
                return cached_data
        
        try:
            # Use ipapi.co for geolocation (free tier)
            async with aiohttp.ClientSession() as session:
                url = f"https://ipapi.co/{ip_address}/json/"
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        location = GeoLocation(
                            latitude=float(data.get('latitude', 0)),
                            longitude=float(data.get('longitude', 0)),
                            country=data.get('country_name', ''),
                            city=data.get('city', ''),
                            region=data.get('region', ''),
                            timezone=data.get('timezone', ''),
                            isp=data.get('org', '')
                        )
                        
                        # Cache the result
                        self.cache[ip_address] = (location, time.time())
                        return location
                        
        except Exception as e:
            self.logger.error(f"Failed to get geolocation for {ip_address}: {e}")
            
        return None
    
    async def get_local_location(self) -> Optional[GeoLocation]:
        """Get current system's geolocation"""
        try:
            # Get public IP first
            async with aiohttp.ClientSession() as session:
                async with session.get('https://ipapi.co/ip/', timeout=10) as response:
                    if response.status == 200:
                        public_ip = await response.text()
                        return await self.get_location_by_ip(public_ip.strip())
        except Exception as e:
            self.logger.error(f"Failed to get local location: {e}")
            
        return None

class NetworkMetricsCollector:
    """Collect network performance metrics"""
    
    def __init__(self):
        self.metrics_history = []
        self.max_history = 100
        self.logger = logging.getLogger(__name__)
        
    async def measure_latency(self, target_ip: str, port: int = 80) -> float:
        """Measure network latency to a target"""
        try:
            start_time = time.time()
            
            # Create a socket connection
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            
            result = sock.connect_ex((target_ip, port))
            
            end_time = time.time()
            sock.close()
            
            if result == 0:
                return (end_time - start_time) * 1000  # Convert to milliseconds
            else:
                return float('inf')  # Connection failed
                
        except Exception as e:
            self.logger.error(f"Latency measurement failed for {target_ip}: {e}")
            return float('inf')
    
    async def measure_bandwidth(self, target_url: str = "https://httpbin.org/bytes/1048576") -> float:
        """Measure network bandwidth using HTTP download test"""
        try:
            start_time = time.time()
            
            async with aiohttp.ClientSession() as session:
                async with session.get(target_url, timeout=30) as response:
                    if response.status == 200:
                        content = await response.read()
                        end_time = time.time()
                        
                        # Calculate bandwidth in Mbps
                        size_mb = len(content) / (1024 * 1024)
                        time_seconds = end_time - start_time
                        bandwidth = (size_mb * 8) / time_seconds  # Convert to Mbps
                        
                        return bandwidth
                        
        except Exception as e:
            self.logger.error(f"Bandwidth measurement failed for {target_url}: {e}")
            
        return 0.0
    
    def get_system_metrics(self) -> NetworkMetrics:
        """Get current system network metrics"""
        try:
            # Get CPU and memory usage
            cpu_usage = psutil.cpu_percent(interval=1)
            memory_usage = psutil.virtual_memory().percent
            
            # Get network stats
            net_io = psutil.net_io_counters()
            
            # Calculate network load (simplified)
            network_load = min(100, (net_io.bytes_sent + net_io.bytes_recv) / (1024 * 1024) * 10)
            
            # Get uptime
            boot_time = psutil.boot_time()
            uptime_seconds = time.time() - boot_time
            uptime_percentage = min(100, (uptime_seconds / (24 * 3600)) * 100)  # As percentage of 24 hours
            
            return NetworkMetrics(
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
                network_load=network_load,
                uptime=uptime_percentage,
                last_updated=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Failed to get system metrics: {e}")
            return NetworkMetrics()

class AdvancedNodeDiscovery:
    """Advanced node discovery with geolocation and network metrics"""
    
    def __init__(self):
        self.discovered_nodes: Dict[str, AdvancedMeshNode] = {}
        self.geolocation_service = GeolocationService()
        self.metrics_collector = NetworkMetricsCollector()
        self.bootstrap_nodes = [
            {"host": "127.0.0.1", "port": 8000},
            {"host": "127.0.0.1", "port": 8001},
            {"host": "127.0.0.1", "port": 8002}
        ]
        self.logger = logging.getLogger(__name__)
        self.discovery_radius = 5000  # km
        self.max_nodes_per_region = 10
        
    async def discover_nodes(self, local_node: AdvancedMeshNode) -> List[AdvancedMeshNode]:
        """Discover nodes using advanced geolocation and network metrics"""
        discovered = []
        
        # Ensure local node has location
        if not local_node.location or (local_node.location.latitude == 0 and local_node.location.longitude == 0):
            local_node.location = await self.geolocation_service.get_local_location()
            if not local_node.location:
                local_node.location = GeoLocation(0.0, 0.0)  # Fallback
        
        # Update local node metrics
        local_node.metrics = self.metrics_collector.get_system_metrics()
        
        # Discover nodes from bootstrap list
        for bootstrap in self.bootstrap_nodes:
            if bootstrap["host"] == local_node.host and bootstrap["port"] == local_node.port:
                continue  # Skip self
                
            node = await self._probe_node(bootstrap["host"], bootstrap["port"])
            if node:
                discovered.append(node)
        
        # Discover nodes from existing connections
        for existing_node in self.discovered_nodes.values():
            if existing_node.id == local_node.id:
                continue
                
            # Check if node is within discovery radius
            if local_node.location and existing_node.location:
                distance = local_node.location.distance_to(existing_node.location)
                if distance <= self.discovery_radius:
                    # Test connectivity
                    latency = await self.metrics_collector.measure_latency(
                        existing_node.host, existing_node.port
                    )
                    
                    if latency < 1000:  # Less than 1 second
                        existing_node.metrics.latency = latency
                        discovered.append(existing_node)
        
        # Optimize discovered nodes based on network metrics and location
        optimized_nodes = await self._optimize_node_selection(local_node, discovered)
        
        # Update discovered nodes cache
        for node in optimized_nodes:
            self.discovered_nodes[node.id] = node
        
        return optimized_nodes
    
    async def _probe_node(self, host: str, port: int) -> Optional[AdvancedMeshNode]:
        """Probe a node to gather information"""
        try:
            # Test basic connectivity
            latency = await self.metrics_collector.measure_latency(host, port)
            if latency == float('inf'):
                return None
            
            # Get geolocation for the node
            location = await self.geolocation_service.get_location_by_ip(host)
            if not location:
                location = GeoLocation(0.0, 0.0)
            
            # Create node with gathered information
            node_id = f"{host}:{port}"
            node = AdvancedMeshNode(
                id=node_id,
                host=host,
                port=port,
                location=location,
                metrics=NetworkMetrics(
                    latency=latency,
                    last_updated=datetime.now()
                ),
                capabilities=NodeCapabilities(),
                last_seen=time.time()
            )
            
            self.logger.info(f"Probed node {node_id} - Latency: {latency}ms, Location: {location.city}, {location.country}")
            return node
            
        except Exception as e:
            self.logger.error(f"Failed to probe node {host}:{port}: {e}")
            return None
    
    async def _optimize_node_selection(self, local_node: AdvancedMeshNode, candidates: List[AdvancedMeshNode]) -> List[AdvancedMeshNode]:
        """Optimize node selection based on multiple factors"""
        if not candidates:
            return []
        
        # Score each candidate node
        scored_nodes = []
        for candidate in candidates:
            score = await self._calculate_node_score(local_node, candidate)
            scored_nodes.append((score, candidate))
        
        # Sort by score (higher is better)
        scored_nodes.sort(key=lambda x: x[0], reverse=True)
        
        # Select top nodes with geographical diversity
        selected = []
        regions_used = set()
        
        for score, node in scored_nodes:
            if len(selected) >= 10:  # Max connections
                break
                
            region_key = f"{node.location.country}:{node.location.region}"
            
            # Ensure geographical diversity
            if region_key not in regions_used or len(selected) < 3:
                selected.append(node)
                regions_used.add(region_key)
        
        return selected
    
    async def _calculate_node_score(self, local_node: AdvancedMeshNode, candidate: AdvancedMeshNode) -> float:
        """Calculate a score for a candidate node"""
        score = 0.0
        
        # Network quality score (40% weight)
        quality_score = candidate.metrics.calculate_quality_score()
        score += quality_score * 0.4
        
        # Distance score (20% weight) - closer is better for latency
        if local_node.location and candidate.location:
            distance = local_node.location.distance_to(candidate.location)
            # Normalize distance score (closer = higher score)
            distance_score = max(0, 1 - (distance / 20000))  # 20,000 km max distance
            score += distance_score * 0.2
        
        # Trust score (20% weight) - trust-first principle
        score += candidate.trust_score * 0.2
        
        # Capabilities score (10% weight)
        capabilities_score = len(candidate.capabilities.supported_protocols) / 5.0
        score += capabilities_score * 0.1
        
        # Uptime score (10% weight)
        uptime_score = candidate.metrics.uptime / 100.0
        score += uptime_score * 0.1
        
        return min(1.0, max(0.0, score))
    
    async def get_optimal_bootstrap_nodes(self, count: int = 3) -> List[Dict[str, Any]]:
        """Get optimal bootstrap nodes for new nodes joining the network"""
        if len(self.discovered_nodes) < count:
            return self.bootstrap_nodes[:count]
        
        # Select nodes with best network metrics and geographical distribution
        nodes = list(self.discovered_nodes.values())
        
        # Sort by network quality
        nodes.sort(key=lambda n: n.metrics.calculate_quality_score(), reverse=True)
        
        # Select with geographical diversity
        selected = []
        regions_used = set()
        
        for node in nodes:
            if len(selected) >= count:
                break
                
            region_key = f"{node.location.country}:{node.location.region}"
            
            if region_key not in regions_used or len(selected) < count // 2:
                selected.append({
                    "host": node.host,
                    "port": node.port,
                    "location": {
                        "country": node.location.country,
                        "city": node.location.city
                    },
                    "quality_score": node.metrics.calculate_quality_score()
                })
                regions_used.add(region_key)
        
        return selected
    
    async def update_node_metrics(self, node_id: str):
        """Update metrics for a specific node"""
        if node_id not in self.discovered_nodes:
            return
        
        node = self.discovered_nodes[node_id]
        
        # Update network metrics
        latency = await self.metrics_collector.measure_latency(node.host, node.port)
        if latency != float('inf'):
            node.metrics.latency = latency
            node.metrics.last_updated = datetime.now()
            node.last_seen = time.time()
        
        # Update system metrics if it's a local node
        if node.host in ['127.0.0.1', 'localhost']:
            system_metrics = self.metrics_collector.get_system_metrics()
            node.metrics.cpu_usage = system_metrics.cpu_usage
            node.metrics.memory_usage = system_metrics.memory_usage
            node.metrics.network_load = system_metrics.network_load
            node.metrics.uptime = system_metrics.uptime
    
    def get_network_topology(self) -> Dict[str, Any]:
        """Get network topology information"""
        topology = {
            "total_nodes": len(self.discovered_nodes),
            "nodes_by_region": {},
            "average_latency": 0.0,
            "network_health": 0.0
        }
        
        total_latency = 0.0
        total_quality = 0.0
        
        for node in self.discovered_nodes.values():
            # Group by region
            region_key = f"{node.location.country}:{node.location.region}"
            if region_key not in topology["nodes_by_region"]:
                topology["nodes_by_region"][region_key] = []
            
            topology["nodes_by_region"][region_key].append({
                "id": node.id,
                "host": node.host,
                "port": node.port,
                "latency": node.metrics.latency,
                "quality_score": node.metrics.calculate_quality_score()
            })
            
            total_latency += node.metrics.latency
            total_quality += node.metrics.calculate_quality_score()
        
        if self.discovered_nodes:
            topology["average_latency"] = total_latency / len(self.discovered_nodes)
            topology["network_health"] = total_quality / len(self.discovered_nodes)
        
        return topology

# Example usage and testing
async def main():
    """Example usage of Advanced Node Discovery"""
    logging.basicConfig(level=logging.INFO)
    
    # Create discovery service
    discovery = AdvancedNodeDiscovery()
    
    # Create a local node
    local_node = AdvancedMeshNode(
        id="local_node_001",
        host="127.0.0.1",
        port=8000
    )
    
    print("🌐 Starting Advanced Node Discovery")
    print("=" * 50)
    
    # Discover nodes
    discovered_nodes = await discovery.discover_nodes(local_node)
    
    print(f"✅ Discovered {len(discovered_nodes)} nodes")
    for node in discovered_nodes:
        print(f"  • {node.id} - {node.location.city}, {node.location.country}")
        print(f"    Latency: {node.metrics.latency:.2f}ms")
        print(f"    Quality: {node.metrics.calculate_quality_score():.2f}")
    
    # Get optimal bootstrap nodes
    print("\n🚀 Optimal Bootstrap Nodes:")
    bootstrap_nodes = await discovery.get_optimal_bootstrap_nodes(3)
    for i, node in enumerate(bootstrap_nodes, 1):
        print(f"  {i}. {node['host']}:{node['port']}")
        if 'location' in node:
            print(f"     Location: {node['location']['city']}, {node['location']['country']}")
        if 'quality_score' in node:
            print(f"     Quality: {node['quality_score']:.2f}")
    
    # Show network topology
    print("\n📊 Network Topology:")
    topology = discovery.get_network_topology()
    print(f"  Total Nodes: {topology['total_nodes']}")
    print(f"  Average Latency: {topology['average_latency']:.2f}ms")
    print(f"  Network Health: {topology['network_health']:.2f}")
    
    print("\n🎯 Advanced Node Discovery Complete!")

if __name__ == "__main__":
    asyncio.run(main())
