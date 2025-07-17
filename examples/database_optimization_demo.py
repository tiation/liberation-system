#!/usr/bin/env python3
"""
Database Optimization Demo
Demonstrates the use of indexing, materialized views, and caching for the Liberation System
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add the parent directory to the path
sys.path.append(str(Path(__file__).parent.parent))

from core.database_optimization import (
    get_optimized_database_manager,
    close_optimized_database_manager,
    CacheConfig
)
from mesh.optimized_mesh_storage import (
    get_mesh_storage,
    close_mesh_storage,
    MeshStorageConfig
)
from mesh.Mesh_Network.Advanced_Node_Discovery import (
    AdvancedMeshNode,
    GeoLocation,
    NetworkMetrics,
    NodeCapabilities,
    NodeType
)
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress


async def demo_database_optimization():
    """Demonstrate database optimization features"""
    console = Console()
    
    console.print(Panel.fit(
        "🚀 Liberation System Database Optimization Demo",
        style="bold cyan"
    ))
    
    try:
        # Initialize optimized database manager
        console.print("\n[cyan]Step 1: Initializing Optimized Database Manager[/cyan]")
        db_manager = await get_optimized_database_manager()
        
        # Demonstrate caching with human statistics
        console.print("\n[cyan]Step 2: Demonstrating Cached Statistics[/cyan]")
        
        start_time = time.time()
        human_stats = await db_manager.get_human_stats()
        first_query_time = time.time() - start_time
        
        start_time = time.time()
        human_stats_cached = await db_manager.get_human_stats()
        cached_query_time = time.time() - start_time
        
        # Display performance improvement
        performance_table = Table(title="Cache Performance Comparison")
        performance_table.add_column("Query Type", style="cyan")
        performance_table.add_column("Time (ms)", style="green")
        performance_table.add_column("Improvement", style="yellow")
        
        performance_table.add_row(
            "First Query (DB)",
            f"{first_query_time * 1000:.2f}",
            "Baseline"
        )
        performance_table.add_row(
            "Cached Query",
            f"{cached_query_time * 1000:.2f}",
            f"{((first_query_time - cached_query_time) / first_query_time * 100):.1f}% faster"
        )
        
        console.print(performance_table)
        
        # Show human statistics
        if human_stats:
            stats_table = Table(title="Human Statistics (Cached)")
            stats_table.add_column("Metric", style="cyan")
            stats_table.add_column("Value", style="green")
            
            for key, value in human_stats.items():
                stats_table.add_row(key.replace('_', ' ').title(), str(value))
            
            console.print(stats_table)
        
        # Demonstrate transaction summary
        console.print("\n[cyan]Step 3: Demonstrating Transaction Summary[/cyan]")
        
        transaction_summary = await db_manager.get_transaction_summary(days=7)
        
        if transaction_summary:
            trans_table = Table(title="Transaction Summary (Last 7 Days)")
            trans_table.add_column("Date", style="cyan")
            trans_table.add_column("Type", style="green")
            trans_table.add_column("Status", style="yellow")
            trans_table.add_column("Count", style="magenta")
            trans_table.add_column("Total Amount", style="red")
            
            for summary in transaction_summary[:10]:  # Show first 10
                trans_table.add_row(
                    str(summary.get('transaction_date', 'N/A')),
                    summary.get('transaction_type', 'N/A'),
                    summary.get('status', 'N/A'),
                    str(summary.get('transaction_count', 0)),
                    f"${summary.get('total_amount', 0):,.2f}"
                )
            
            console.print(trans_table)
        
        # Demonstrate knowledge statistics
        console.print("\n[cyan]Step 4: Demonstrating Knowledge Statistics[/cyan]")
        
        knowledge_stats = await db_manager.get_knowledge_stats()
        
        if knowledge_stats and 'knowledge_stats' in knowledge_stats:
            knowledge_table = Table(title="Knowledge Base Statistics")
            knowledge_table.add_column("Type", style="cyan")
            knowledge_table.add_column("Status", style="green")
            knowledge_table.add_column("Count", style="yellow")
            knowledge_table.add_column("Avg Confidence", style="magenta")
            knowledge_table.add_column("Avg Effectiveness", style="red")
            
            for stat in knowledge_stats['knowledge_stats']:
                knowledge_table.add_row(
                    stat.get('knowledge_type', 'N/A'),
                    stat.get('status', 'N/A'),
                    str(stat.get('entry_count', 0)),
                    f"{stat.get('avg_confidence', 0):.2f}",
                    f"{stat.get('avg_effectiveness', 0):.2f}"
                )
            
            console.print(knowledge_table)
        
        # Cache invalidation demo
        console.print("\n[cyan]Step 5: Demonstrating Cache Invalidation[/cyan]")
        
        await db_manager.invalidate_cache("human_stats*")
        console.print("✅ Cache invalidated for pattern: human_stats*")
        
        # Re-query to show cache miss
        start_time = time.time()
        human_stats_fresh = await db_manager.get_human_stats()
        fresh_query_time = time.time() - start_time
        
        console.print(f"Fresh query after invalidation: {fresh_query_time * 1000:.2f}ms")
        
    except Exception as e:
        console.print(f"[red]❌ Database optimization demo failed: {e}[/red]")
        raise
    
    finally:
        await close_optimized_database_manager()


async def demo_mesh_storage_optimization():
    """Demonstrate mesh network storage optimization"""
    console = Console()
    
    console.print(Panel.fit(
        "🌐 Mesh Network Storage Optimization Demo",
        style="bold green"
    ))
    
    try:
        # Initialize mesh storage
        console.print("\n[cyan]Step 1: Initializing Optimized Mesh Storage[/cyan]")
        mesh_storage = await get_mesh_storage()
        
        # Create sample nodes
        console.print("\n[cyan]Step 2: Creating Sample Mesh Nodes[/cyan]")
        
        sample_nodes = []
        locations = [
            ("US", "California", "San Francisco", 37.7749, -122.4194),
            ("US", "New York", "New York", 40.7128, -74.0060),
            ("UK", "England", "London", 51.5074, -0.1278),
            ("DE", "Bavaria", "Munich", 48.1351, 11.5820),
            ("JP", "Tokyo", "Tokyo", 35.6762, 139.6503)
        ]
        
        with Progress() as progress:
            task = progress.add_task("Creating nodes...", total=len(locations))
            
            for i, (country, region, city, lat, lon) in enumerate(locations):
                node = AdvancedMeshNode(
                    id=f"node_{i:03d}",
                    host=f"10.0.{i}.1",
                    port=8000 + i,
                    node_type=NodeType.STANDARD,
                    location=GeoLocation(
                        latitude=lat,
                        longitude=lon,
                        country=country,
                        region=region,
                        city=city
                    ),
                    metrics=NetworkMetrics(
                        latency=50 + i * 10,
                        bandwidth=100 + i * 20,
                        packet_loss=0.1 + i * 0.05,
                        uptime=95 + i,
                        last_updated=datetime.now()
                    ),
                    capabilities=NodeCapabilities(
                        max_connections=50 + i * 10,
                        storage_capacity=1000 + i * 500,
                        trust_level=0.8 + i * 0.04
                    ),
                    status="active",
                    trust_score=0.8 + i * 0.04
                )
                
                sample_nodes.append(node)
                await mesh_storage.store_node(node)
                progress.advance(task)
        
        console.print(f"✅ Created and stored {len(sample_nodes)} sample nodes")
        
        # Demonstrate cached node retrieval
        console.print("\n[cyan]Step 3: Demonstrating Cached Node Retrieval[/cyan]")
        
        # First query (database)
        start_time = time.time()
        node = await mesh_storage.get_node("node_000")
        first_query_time = time.time() - start_time
        
        # Second query (cache)
        start_time = time.time()
        node_cached = await mesh_storage.get_node("node_000")
        cached_query_time = time.time() - start_time
        
        # Display performance
        mesh_performance_table = Table(title="Mesh Node Cache Performance")
        mesh_performance_table.add_column("Query Type", style="cyan")
        mesh_performance_table.add_column("Time (ms)", style="green")
        mesh_performance_table.add_column("Improvement", style="yellow")
        
        mesh_performance_table.add_row(
            "First Query (DB)",
            f"{first_query_time * 1000:.2f}",
            "Baseline"
        )
        mesh_performance_table.add_row(
            "Cached Query",
            f"{cached_query_time * 1000:.2f}",
            f"{((first_query_time - cached_query_time) / first_query_time * 100):.1f}% faster"
        )
        
        console.print(mesh_performance_table)
        
        # Demonstrate regional queries
        console.print("\n[cyan]Step 4: Demonstrating Regional Node Queries[/cyan]")
        
        us_nodes = await mesh_storage.get_nodes_by_region("US")
        uk_nodes = await mesh_storage.get_nodes_by_region("UK")
        
        region_table = Table(title="Nodes by Region")
        region_table.add_column("Region", style="cyan")
        region_table.add_column("Node Count", style="green")
        region_table.add_column("Sample Node", style="yellow")
        
        region_table.add_row("US", str(len(us_nodes)), us_nodes[0].id if us_nodes else "None")
        region_table.add_row("UK", str(len(uk_nodes)), uk_nodes[0].id if uk_nodes else "None")
        
        console.print(region_table)
        
        # Demonstrate network topology
        console.print("\n[cyan]Step 5: Demonstrating Network Topology[/cyan]")
        
        topology = await mesh_storage.get_network_topology()
        
        if topology and 'regions' in topology:
            topology_table = Table(title="Network Topology")
            topology_table.add_column("Region", style="cyan")
            topology_table.add_column("Node Count", style="green")
            topology_table.add_column("Avg Latency", style="yellow")
            topology_table.add_column("Avg Trust", style="magenta")
            
            for region_data in topology['regions']:
                region_info = region_data.get('_id', {})
                region_name = f"{region_info.get('country', 'Unknown')}/{region_info.get('region', 'Unknown')}"
                
                topology_table.add_row(
                    region_name,
                    str(region_data.get('node_count', 0)),
                    f"{region_data.get('avg_latency', 0):.1f}ms",
                    f"{region_data.get('avg_trust_score', 0):.2f}"
                )
            
            console.print(topology_table)
        
        # Demonstrate performance statistics
        console.print("\n[cyan]Step 6: Demonstrating Performance Statistics[/cyan]")
        
        perf_stats = await mesh_storage.get_performance_stats()
        
        if perf_stats:
            perf_table = Table(title="Mesh Storage Performance")
            perf_table.add_column("Metric", style="cyan")
            perf_table.add_column("Value", style="green")
            
            for key, value in perf_stats.items():
                if key.endswith('_size'):
                    # Format size in human readable format
                    if value > 1024 * 1024:
                        value = f"{value / (1024 * 1024):.2f} MB"
                    elif value > 1024:
                        value = f"{value / 1024:.2f} KB"
                    else:
                        value = f"{value} bytes"
                
                perf_table.add_row(key.replace('_', ' ').title(), str(value))
            
            console.print(perf_table)
        
    except Exception as e:
        console.print(f"[red]❌ Mesh storage optimization demo failed: {e}[/red]")
        raise
    
    finally:
        await close_mesh_storage()


async def main():
    """Main demo function"""
    console = Console()
    
    console.print(Panel.fit(
        "🎯 Liberation System Database Optimization Demo",
        style="bold blue"
    ))
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        # Demo 1: Database optimization
        await demo_database_optimization()
        
        console.print("\n" + "="*60 + "\n")
        
        # Demo 2: Mesh storage optimization
        await demo_mesh_storage_optimization()
        
        console.print("\n" + Panel.fit(
            "✅ All Database Optimization Demos Completed Successfully!",
            style="bold green"
        ))
        
    except Exception as e:
        console.print(f"\n[red]❌ Demo failed: {e}[/red]")
        raise


if __name__ == "__main__":
    asyncio.run(main())
