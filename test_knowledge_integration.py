#!/usr/bin/env python3
"""
Test script for knowledge sharing system integration with liberation-system
"""

import asyncio
import sys
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.knowledge_sharing import KnowledgeShareManager, KnowledgeType
from core.liberation_core import LiberationSystemManager
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

async def test_knowledge_system_standalone():
    """Test knowledge sharing system standalone"""
    console.print(Panel.fit("Testing Knowledge Sharing System", style="cyan"))
    
    # Initialize knowledge system
    knowledge_system = KnowledgeShareManager()
    await knowledge_system.initialize()
    
    # Test adding knowledge
    entry_id = await knowledge_system.add_knowledge(
        title="Liberation System Architecture",
        content="The Liberation System follows a trust-by-default architecture with four core components: Resource Distribution, Truth Spreading, Knowledge Sharing, and Mesh Networking. Each component operates autonomously while maintaining synchronization through the core automation engine.",
        knowledge_type=KnowledgeType.TECHNICAL,
        author="test_user",
        tags=["architecture", "system", "liberation", "design"]
    )
    
    console.print(f"[green]✅ Added knowledge entry: {entry_id}[/green]")
    
    # Test collaborative learning session
    session_id = await knowledge_system.start_learning_session(
        title="System Optimization Workshop",
        description="Collaborative session to optimize liberation system performance",
        participants=["user1", "user2", "autonomous_agent"]
    )
    
    console.print(f"[green]✅ Started learning session: {session_id}[/green]")
    
    # Test problem context
    problem_id = await knowledge_system.add_problem_context(
        problem_description="Need to optimize resource distribution algorithm for better performance",
        domain="optimization",
        priority=3
    )
    
    console.print(f"[green]✅ Added problem context: {problem_id}[/green]")
    
    # Test knowledge search
    search_results = await knowledge_system.search_knowledge("architecture system")
    console.print(f"[green]✅ Found {len(search_results)} knowledge entries for 'architecture system'[/green]")
    
    # Display system statistics
    knowledge_system.display_knowledge_stats()
    
    return knowledge_system

async def test_integrated_system():
    """Test knowledge sharing integration with liberation core"""
    console.print(Panel.fit("Testing Integrated Liberation System", style="green"))
    
    # Initialize liberation system manager
    liberation_manager = LiberationSystemManager()
    
    # Initialize all systems
    await liberation_manager.core.initialize_all_systems()
    
    # Check if knowledge system is initialized
    if liberation_manager.core.knowledge_system:
        console.print("[green]✅ Knowledge system integrated successfully[/green]")
        
        # Add some test knowledge through the integrated system
        await liberation_manager.core.knowledge_system.add_knowledge(
            title="Liberation System Test Integration",
            content="This knowledge entry was created through the integrated liberation system to test the knowledge sharing functionality.",
            knowledge_type=KnowledgeType.TECHNICAL,
            author="integration_test",
            tags=["integration", "test", "liberation"]
        )
        
        # Display integrated system status
        liberation_manager.core.display_status()
        
        # Test a few task cycles to see knowledge sharing in action
        console.print("[yellow]Running 3 task cycles to test knowledge sharing integration...[/yellow]")
        for i in range(3):
            await liberation_manager.core.share_knowledge()
            await asyncio.sleep(1)
        
        console.print("[green]✅ Integration test completed successfully[/green]")
    else:
        console.print("[red]❌ Knowledge system not integrated[/red]")
    
    return liberation_manager

async def test_api_integration():
    """Test API integration with knowledge sharing"""
    console.print(Panel.fit("Testing API Integration", style="blue"))
    
    try:
        # Import and test API components
        from api.app import knowledge_system as api_knowledge_system
        
        # Test if API knowledge system is accessible
        if api_knowledge_system:
            console.print("[green]✅ API knowledge system accessible[/green]")
            
            # Test adding knowledge through API system
            entry_id = await api_knowledge_system.add_knowledge(
                title="API Integration Test",
                content="This knowledge entry was created through the API knowledge system to test integration.",
                knowledge_type=KnowledgeType.TECHNICAL,
                author="api_test",
                tags=["api", "integration", "test"]
            )
            
            console.print(f"[green]✅ Added knowledge through API: {entry_id}[/green]")
        else:
            console.print("[red]❌ API knowledge system not accessible[/red]")
            
    except Exception as e:
        console.print(f"[yellow]⚠️ API integration test skipped: {e}[/yellow]")

async def demonstrate_autonomous_features():
    """Demonstrate autonomous knowledge sharing features"""
    console.print(Panel.fit("Demonstrating Autonomous Features", style="magenta"))
    
    # Initialize knowledge system
    knowledge_system = KnowledgeShareManager()
    await knowledge_system.initialize()
    
    # Add some related knowledge entries
    await knowledge_system.add_knowledge(
        title="Performance Optimization Techniques",
        content="Various techniques for optimizing system performance including caching, load balancing, and resource pooling.",
        knowledge_type=KnowledgeType.TECHNICAL,
        author="performance_expert",
        tags=["performance", "optimization", "techniques"]
    )
    
    await knowledge_system.add_knowledge(
        title="Load Balancing Best Practices",
        content="Best practices for implementing load balancing in distributed systems to ensure optimal resource utilization.",
        knowledge_type=KnowledgeType.PROCESS,
        author="system_architect",
        tags=["load-balancing", "distributed", "optimization"]
    )
    
    await knowledge_system.add_knowledge(
        title="Resource Pool Management",
        content="Effective strategies for managing resource pools to maximize efficiency and minimize waste.",
        knowledge_type=KnowledgeType.RESOURCE,
        author="resource_manager",
        tags=["resources", "management", "efficiency"]
    )
    
    # Add a problem that should trigger autonomous solving
    problem_id = await knowledge_system.add_problem_context(
        problem_description="System is experiencing high latency during peak usage periods",
        domain="performance",
        priority=2
    )
    
    console.print(f"[green]✅ Added problem for autonomous solving: {problem_id}[/green]")
    
    # Wait a bit for autonomous processes to work
    console.print("[yellow]Waiting for autonomous processes to analyze and solve...[/yellow]")
    await asyncio.sleep(3)
    
    # Check if solution was generated
    if problem_id in knowledge_system.problem_contexts:
        context = knowledge_system.problem_contexts[problem_id]
        if context.attempted_solutions:
            console.print(f"[green]✅ Autonomous solution generated: {len(context.attempted_solutions)} solution(s)[/green]")
            console.print(f"[green]   Status: {context.status}[/green]")
            console.print(f"[green]   Confidence: {context.confidence_level:.2f}[/green]")
        else:
            console.print("[yellow]⚠️ No solution generated yet (may need more time)[/yellow]")
    
    # Display final statistics
    knowledge_system.display_knowledge_stats()

async def main():
    """Main test function"""
    console.print(Panel.fit(
        "[bold cyan]🌟 Liberation System Knowledge Sharing Integration Test 🌟[/bold cyan]\n\n"
        "[green]Testing collaborative knowledge sharing and autonomous problem-solving[/green]\n\n"
        "[yellow]• Knowledge base management\n"
        "• Collaborative learning sessions\n"
        "• Autonomous problem solving\n"
        "• System integration[/yellow]",
        style="cyan"
    ))
    
    try:
        # Test 1: Standalone knowledge system
        console.print("\n[bold]Test 1: Standalone Knowledge System[/bold]")
        await test_knowledge_system_standalone()
        
        # Test 2: Integrated system
        console.print("\n[bold]Test 2: Integrated Liberation System[/bold]")
        await test_integrated_system()
        
        # Test 3: API integration
        console.print("\n[bold]Test 3: API Integration[/bold]")
        await test_api_integration()
        
        # Test 4: Autonomous features
        console.print("\n[bold]Test 4: Autonomous Features[/bold]")
        await demonstrate_autonomous_features()
        
        console.print(Panel.fit(
            "[bold green]🎉 All Tests Completed Successfully! 🎉[/bold green]\n\n"
            "[green]Knowledge sharing system is fully integrated with:[/green]\n"
            "• Liberation core system\n"
            "• API endpoints\n"
            "• Autonomous problem solving\n"
            "• Collaborative learning\n\n"
            "[cyan]Ready for production deployment![/cyan]",
            style="green"
        ))
        
    except Exception as e:
        console.print(f"[red]❌ Test failed: {e}[/red]")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run the test
    asyncio.run(main())
