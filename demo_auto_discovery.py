#!/usr/bin/env python3
"""
Demo script for automatic node discovery and registration
Shows how nodes can be automatically added to the load balancer through messages
"""

import asyncio
import logging
from core.system_integration import LiberationSystemIntegrator
from core.auto_node_discovery import NodeDiscoveryMethod
from rich.console import Console
from rich.panel import Panel

async def demo_auto_discovery():
    """Demonstrate automatic node discovery and registration"""
    console = Console()
    
    # Display demo header
    console.print(Panel.fit(
        "[bold cyan]🔍 AUTO NODE DISCOVERY DEMO 🔍[/bold cyan]\n\n"
        "[green]This demo shows how nodes can be automatically discovered[/green]\n"
        "[green]and registered with the load balancer through messages.[/green]\n\n"
        "[yellow]• Nodes announce themselves via broadcast/multicast[/yellow]\n"
        "[yellow]• System validates node capabilities and health[/yellow]\n"
        "[yellow]• Load balancer automatically registers healthy nodes[/yellow]\n"
        "[yellow]• Real-time dashboard shows discovery activity[/yellow]",
        style="cyan"
    ))
    
    # Initialize the integrated system
    console.print("\n🚀 [cyan]Starting Liberation System with Auto Discovery...[/cyan]")
    integrator = LiberationSystemIntegrator()
    await integrator.initialize()
    
    # Wait for initial system startup
    await asyncio.sleep(2)
    
    # Display initial status
    console.print("\n📊 [green]Initial System Status:[/green]")
    integrator.display_integrated_dashboard()
    
    # Demonstrate node announcements
    console.print("\n📢 [cyan]Announcing new nodes to the network...[/cyan]")
    
    # Announce mesh nodes
    for i in range(2):
        node_info = {
            'node_id': f'dynamic_mesh_node_{i}',
            'node_type': 'mesh',
            'host': 'localhost',
            'port': 8100 + i,
            'capabilities': ['mesh_communication', 'truth_spreading'],
            'load_balancer_compatible': True,
            'mesh_compatible': True,
            'system_version': '1.0.0',
            'metadata': {
                'max_connections': 800,
                'max_cpu_usage': 75.0,
                'max_memory_usage': 80.0,
                'weight': 1.2
            }
        }
        
        await integrator.announce_node_to_network(node_info, NodeDiscoveryMethod.BROADCAST)
        await asyncio.sleep(1)
    
    # Announce resource nodes
    for i in range(1):
        node_info = {
            'node_id': f'dynamic_resource_node_{i}',
            'node_type': 'resource',
            'host': 'localhost',
            'port': 9100 + i,
            'capabilities': ['resource_distribution'],
            'load_balancer_compatible': True,
            'mesh_compatible': False,
            'system_version': '1.0.0',
            'metadata': {
                'max_connections': 1200,
                'max_cpu_usage': 85.0,
                'max_memory_usage': 90.0,
                'weight': 0.9
            }
        }
        
        await integrator.announce_node_to_network(node_info, NodeDiscoveryMethod.MULTICAST)
        await asyncio.sleep(1)
    
    # Wait for nodes to be processed
    console.print("\n⏳ [yellow]Waiting for node validation and registration...[/yellow]")
    await asyncio.sleep(10)
    
    # Display discovery statistics
    console.print("\n📈 [green]Discovery Statistics:[/green]")
    integrator.display_discovery_dashboard()
    
    # Display updated system status
    console.print("\n📊 [green]Updated System Status:[/green]")
    integrator.display_integrated_dashboard()
    
    # Test task submission to dynamically added nodes
    console.print("\n🎯 [cyan]Testing task submission to dynamically added nodes...[/cyan]")
    
    # Submit tasks that will be distributed across all nodes (original + discovered)
    for i in range(5):
        await integrator.submit_system_task('mesh_communication', {
            'message_data': {'test_message': f'Auto discovery test {i}'},
            'message_type': 'data'
        })
    
    for i in range(3):
        await integrator.submit_system_task('resource_distribution', {
            'human_id': f'dynamic_human_{i}'
        })
    
    # Display final load balancer status
    console.print("\n🔄 [green]Load Balancer Status After Auto Discovery:[/green]")
    integrator.load_balancer_manager.load_balancer.display_dashboard()
    
    # Display summary
    console.print(Panel.fit(
        "[bold green]✅ AUTO DISCOVERY DEMO COMPLETE ✅[/bold green]\n\n"
        "[cyan]Key Features Demonstrated:[/cyan]\n"
        "[green]• Automatic node discovery via broadcast/multicast[/green]\n"
        "[green]• Real-time node validation and health checking[/green]\n"
        "[green]• Dynamic registration with load balancer[/green]\n"
        "[green]• Seamless integration with existing nodes[/green]\n"
        "[green]• Enterprise-grade monitoring and dashboards[/green]\n\n"
        "[yellow]Nodes can now be added automatically through messages![/yellow]",
        style="green"
    ))
    
    # Keep running for a bit to show continuous operation
    console.print("\n⏰ [yellow]System will continue running for 30 seconds...[/yellow]")
    await asyncio.sleep(30)
    
    # Shutdown
    await integrator.shutdown()
    console.print("\n👋 [green]Demo completed successfully![/green]")

if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        asyncio.run(demo_auto_discovery())
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"❌ Demo failed: {e}")
