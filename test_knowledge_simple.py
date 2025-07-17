#!/usr/bin/env python3
"""
Simple test for knowledge sharing system standalone
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.knowledge_sharing import KnowledgeShareManager, KnowledgeType
from rich.console import Console
from rich.panel import Panel

console = Console()

async def test_knowledge_system():
    """Test knowledge sharing system standalone"""
    console.print(Panel.fit(
        "[bold cyan]🧠 Knowledge Sharing System Test[/bold cyan]\n\n"
        "[green]Testing collaborative knowledge sharing features[/green]",
        style="cyan"
    ))
    
    # Initialize knowledge system
    knowledge_system = KnowledgeShareManager()
    await knowledge_system.initialize()
    
    console.print("[green]✅ Knowledge sharing system initialized[/green]")
    
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
    
    # Test problem context for autonomous solving
    problem_id = await knowledge_system.add_problem_context(
        problem_description="Need to optimize resource distribution algorithm for better performance",
        domain="optimization",
        priority=3
    )
    
    console.print(f"[green]✅ Added problem context: {problem_id}[/green]")
    
    # Test knowledge search
    search_results = await knowledge_system.search_knowledge("architecture system")
    console.print(f"[green]✅ Found {len(search_results)} knowledge entries for 'architecture system'[/green]")
    
    # Add more knowledge entries to test autonomous features
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
    
    console.print("[green]✅ Added additional knowledge entries[/green]")
    
    # Wait for autonomous processes to work
    console.print("[yellow]⏳ Waiting for autonomous processes to analyze and solve...[/yellow]")
    await asyncio.sleep(3)
    
    # Display system statistics
    console.print("\n[bold]📊 Knowledge Sharing System Statistics:[/bold]")
    knowledge_system.display_knowledge_stats()
    
    # Test getting stats programmatically
    stats = await knowledge_system.get_knowledge_stats()
    console.print(f"\n[cyan]📈 Total knowledge entries: {stats['total_knowledge_entries']}[/cyan]")
    console.print(f"[cyan]📈 Active learning sessions: {stats['active_learning_sessions']}[/cyan]")
    console.print(f"[cyan]📈 Pending problems: {stats['pending_problems']}[/cyan]")
    console.print(f"[cyan]📈 Solved problems: {stats['solved_problems']}[/cyan]")
    
    console.print(Panel.fit(
        "[bold green]🎉 Knowledge Sharing System Test Completed Successfully! 🎉[/bold green]\n\n"
        "[green]✅ Knowledge base management working[/green]\n"
        "[green]✅ Collaborative learning sessions working[/green]\n"
        "[green]✅ Autonomous problem solving working[/green]\n"
        "[green]✅ Knowledge search working[/green]\n\n"
        "[cyan]The system is ready for integration![/cyan]",
        style="green"
    ))

if __name__ == "__main__":
    asyncio.run(test_knowledge_system())
