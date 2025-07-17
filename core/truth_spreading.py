"""
Liberation System - Truth Spreading Module
Responsible for managing and orchestrating the truth-spreading mechanism in the system.
"""

import asyncio
import logging
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime
import random


@dataclass
class TruthChannel:
    """Data structure representing a truth channel"""
    channel_id: str
    subscribers: List[str]
    spreading_interval: int = 1800  # 30 minutes
    last_spread: Optional[datetime] = None


class TruthManager:
    """Manages truth spreading within channels"""
    
    def __init__(self):
        self.channels: List[TruthChannel] = []
        self.max_channels: int = 100
        self.logger = logging.getLogger(__name__)
        
    async def initialize(self):
        """Initialize the truth spreading system"""
        self.logger.info("🔄 Initializing Truth Spreading System")
        
        # Initialize default channel
        self.add_channel("default_channel")
        
    async def spread_truth(self, channel_id: str) -> bool:
        """Spread truth within a channel"""
        try:
            # Find channel
            channel = next((ch for ch in self.channels if ch.channel_id == channel_id), None)
            if not channel:
                self.logger.error(f"❌ Channel {channel_id} not found")
                return False
                
            # Check if it's time to spread
            now = datetime.now()
            if channel.last_spread:
                elapsed_time = (now - channel.last_spread).total_seconds()
                if elapsed_time < channel.spreading_interval:
                    self.logger.info(f"⏱️ Not time to spread yet in channel {channel_id}")
                    return False

            # Simulate spreading truth
            self.logger.info(f"📡 Spreading truth in channel {channel_id}")
            self.logger.info(f"🚀 {len(channel.subscribers)} subscribers reached")
            
            # Record spread time
            channel.last_spread = now
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error spreading truth in channel {channel_id}: {e}")
            return False
            
    def add_channel(self, channel_id: str) -> bool:
        """Add a new truth channel"""
        try:
            if any(ch.channel_id == channel_id for ch in self.channels):
                self.logger.warning(f"⚠️ Channel {channel_id} already exists")
                return False
                
            if len(self.channels) >= self.max_channels:
                self.logger.warning(f"⚠️ Maximum number of channels reached")
                return False
                
            # Add new channel
            new_channel = TruthChannel(
                channel_id=channel_id,
                subscribers=[]
            )
            self.channels.append(new_channel)
            self.logger.info(f"✅ Channel {channel_id} added")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error adding channel {channel_id}: {e}")
            return False
            
    def subscribe_to_channel(self, channel_id: str, subscriber_id: str) -> bool:
        """Subscribe a user to a channel"""
        try:
            # Find channel
            channel = next((ch for ch in self.channels if ch.channel_id == channel_id), None)
            if not channel:
                self.logger.error(f"❌ Channel {channel_id} not found")
                return False
                
            if subscriber_id in channel.subscribers:
                self.logger.warning(f"⚠️ Subscriber {subscriber_id} already in channel {channel_id}")
                return False
                
            # Add subscriber
            channel.subscribers.append(subscriber_id)
            self.logger.info(f"✅ Subscriber {subscriber_id} added to channel {channel_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error subscribing to channel {channel_id}: {e}")
            return False


# Global truth manager instance
truth_manager = TruthManager()


async def initialize_truth_spreading():
    """Initialize the global truth manager"""
    await truth_manager.initialize()


async def main():
    """Main function for testing"""
    await initialize_truth_spreading()
    
    # Test adding channels
    truth_manager.add_channel("science_truths")
    
    # Test subscribing
    truth_manager.subscribe_to_channel("science_truths", "user456")
    
    # Test spreading truth
    success = await truth_manager.spread_truth("science_truths")
    print(f"Truth spreading successful: {success}")


if __name__ == "__main__":
    asyncio.run(main())

