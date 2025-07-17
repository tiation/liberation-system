# transformation/truth_spreader.py

import asyncio
import logging
import aiohttp
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import aiofiles
from rich.console import Console
from rich.progress import Progress
from rich.table import Table

@dataclass
class TruthMessage:
    """A message containing truth to spread"""
    id: str
    content: str
    source: str
    priority: int = 1
    created_at: datetime = None
    spread_count: int = 0
    effectiveness_score: float = 0.0
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class Channel:
    """A communication channel to transform"""
    id: str
    name: str
    type: str  # 'billboard', 'social', 'media', 'direct'
    reach: int
    conversion_rate: float = 0.0
    last_message: Optional[TruthMessage] = None
    status: str = 'active'
    
class TruthSpreader:
    """Replace marketing with reality"""
    
    def __init__(self):
        self.console = Console()
        self.logger = logging.getLogger(__name__)
        self.channels: Dict[str, Channel] = {}
        self.truth_messages: List[TruthMessage] = []
        self.spread_count = 0
        self.total_reach = 0
        self.data_dir = Path('data')
        self.data_dir.mkdir(exist_ok=True)
        
    async def initialize(self):
        """Initialize the truth spreading system"""
        try:
            await self._load_channels()
            await self._load_truth_messages()
            self.console.print("🌟 Truth Spreading System initialized", style="cyan")
        except Exception as e:
            self.logger.error(f"Failed to initialize truth spreader: {e}")
            raise
    
    async def _load_channels(self):
        """Load available channels for truth spreading"""
        default_channels = [
            Channel("billboard_001", "Downtown Billboard Network", "billboard", 50000),
            Channel("social_001", "Social Media Feeds", "social", 100000),
            Channel("media_001", "Local Media Outlets", "media", 25000),
            Channel("direct_001", "Direct Communication", "direct", 1000),
        ]
        
        for channel in default_channels:
            self.channels[channel.id] = channel
            
        self.console.print(f"✅ Loaded {len(self.channels)} channels for truth spreading")
    
    async def _load_truth_messages(self):
        """Load truth messages to spread"""
        default_messages = [
            TruthMessage(
                "truth_001",
                "We have enough resources for everyone. Scarcity is artificial.",
                "liberation_system",
                priority=1
            ),
            TruthMessage(
                "truth_002",
                "Your weekly $800 flow is ready. No applications needed.",
                "resource_distribution",
                priority=1
            ),
            TruthMessage(
                "truth_003",
                "Community abundance pools: $104K available for housing and growth.",
                "resource_distribution",
                priority=2
            ),
            TruthMessage(
                "truth_004",
                "Marketing exists to create artificial desire. Reality is abundance.",
                "truth_system",
                priority=3
            ),
        ]
        
        self.truth_messages = default_messages
        self.console.print(f"✅ Loaded {len(self.truth_messages)} truth messages")
    
    async def spread_truth(self):
        """Spread truth across all channels"""
        try:
            with Progress() as progress:
                task = progress.add_task("Spreading truth...", total=len(self.channels))
                
                for channel in self.channels.values():
                    if channel.status == 'active':
                        message = self._select_message_for_channel(channel)
                        if message:
                            success = await self._send_to_channel(message, channel)
                            if success:
                                self.spread_count += 1
                                self.total_reach += channel.reach
                                channel.last_message = message
                                message.spread_count += 1
                                
                    progress.advance(task)
                    
            self.console.print(f"✅ Truth spread to {self.spread_count} channels, reaching {self.total_reach:,} people")
            
        except Exception as e:
            self.logger.error(f"Failed to spread truth: {e}")
            # Continue anyway - truth must flow
    
    def _select_message_for_channel(self, channel: Channel) -> Optional[TruthMessage]:
        """Select the best truth message for this channel"""
        # Prioritize high-priority messages
        available_messages = [msg for msg in self.truth_messages if msg.priority <= 2]
        
        if not available_messages:
            return None
            
        # Select message with highest priority and lowest spread count
        return min(available_messages, key=lambda x: (x.priority, x.spread_count))
    
    async def _send_to_channel(self, message: TruthMessage, channel: Channel) -> bool:
        """Send truth message to specific channel"""
        try:
            # Simulate different channel types
            if channel.type == 'billboard':
                await self._hijack_billboard(message, channel)
            elif channel.type == 'social':
                await self._transform_social_feed(message, channel)
            elif channel.type == 'media':
                await self._convert_media_outlet(message, channel)
            elif channel.type == 'direct':
                await self._direct_communication(message, channel)
            
            # Simulate transmission delay
            await asyncio.sleep(0.1)
            
            self.logger.info(f"Sent truth message '{message.content[:50]}...' to {channel.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send to channel {channel.name}: {e}")
            return False
    
    async def _hijack_billboard(self, message: TruthMessage, channel: Channel):
        """Replace billboard ads with truth"""
        self.console.print(f"📢 Billboard {channel.name}: {message.content}")
        
    async def _transform_social_feed(self, message: TruthMessage, channel: Channel):
        """Transform social media feeds"""
        self.console.print(f"📱 Social {channel.name}: {message.content}")
        
    async def _convert_media_outlet(self, message: TruthMessage, channel: Channel):
        """Convert media outlets to truth"""
        self.console.print(f"📺 Media {channel.name}: {message.content}")
        
    async def _direct_communication(self, message: TruthMessage, channel: Channel):
        """Direct truth communication"""
        self.console.print(f"💬 Direct {channel.name}: {message.content}")
    
    async def add_truth_message(self, content: str, source: str, priority: int = 3) -> str:
        """Add new truth message to spread"""
        message_id = f"truth_{len(self.truth_messages) + 1:03d}"
        message = TruthMessage(message_id, content, source, priority)
        self.truth_messages.append(message)
        
        self.console.print(f"✅ Added truth message: {content[:50]}...")
        return message_id
    
    async def get_spread_statistics(self) -> Dict[str, Any]:
        """Get truth spreading statistics"""
        return {
            'total_messages': len(self.truth_messages),
            'active_channels': len([c for c in self.channels.values() if c.status == 'active']),
            'total_spread_count': self.spread_count,
            'total_reach': self.total_reach,
            'top_messages': sorted(self.truth_messages, key=lambda x: x.spread_count, reverse=True)[:3],
            'channel_performance': {c.name: c.conversion_rate for c in self.channels.values()}
        }
    
    def display_dashboard(self):
        """Display truth spreading dashboard"""
        try:
            table = Table(title="Truth Spreading Dashboard")
            
            table.add_column("Channel", style="cyan")
            table.add_column("Type", style="green")
            table.add_column("Reach", style="yellow")
            table.add_column("Last Message", style="magenta")
            table.add_column("Status", style="red")
            
            for channel in self.channels.values():
                last_msg = channel.last_message.content[:30] + "..." if channel.last_message else "None"
                table.add_row(
                    channel.name,
                    channel.type,
                    f"{channel.reach:,}",
                    last_msg,
                    channel.status
                )
            
            self.console.print(table)
            
            # Summary stats
            self.console.print(f"\n📊 Total Messages Spread: {self.spread_count}")
            self.console.print(f"🌍 Total Reach: {self.total_reach:,} people")
            self.console.print(f"✨ Truth Messages Available: {len(self.truth_messages)}")
            
        except Exception as e:
            self.logger.error(f"Failed to display dashboard: {e}")

class TruthSystem:
    """Complete truth spreading system"""
    
    def __init__(self):
        self.spreader = TruthSpreader()
        self.running = True
        self.console = Console()
        self.logger = logging.getLogger(__name__)
        
    async def initialize(self):
        """Initialize the truth system"""
        await self.spreader.initialize()
        self.console.print("🚀 Truth System initialized successfully")
    
    async def run_forever(self):
        """Keep spreading truth continuously"""
        try:
            while self.running:
                self.console.print("📡 Starting truth spreading cycle...")
                await self.spreader.spread_truth()
                
                # Display dashboard
                self.spreader.display_dashboard()
                
                if self.running:
                    self.console.print("⏳ Waiting for next truth cycle...")
                    await asyncio.sleep(30)  # 30 seconds for testing
                    
        except KeyboardInterrupt:
            self.console.print("\n⚠️  Truth spreading stopped by user")
            self.stop()
        except Exception as e:
            self.logger.error(f"Truth system error: {e}")
            self.console.print(f"❌ Truth system error: {e}")
    
    def stop(self):
        """Stop truth spreading"""
        self.running = False
        self.console.print("🛑 Truth spreading stopped")

async def main():
    """Launch truth spreading system"""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    console = Console()
    console.print("🌟 Truth Spreading System Starting...", style="bold cyan")
    
    try:
        system = TruthSystem()
        await system.initialize()
        await system.run_forever()
        
    except KeyboardInterrupt:
        console.print("\n👋 Truth system shutting down gracefully...")
    except Exception as e:
        console.print(f"❌ Truth system failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
