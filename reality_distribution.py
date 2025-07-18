#!/usr/bin/env python3
"""
💰 Liberation System - Real-World Resource Distribution
This module implements actual resource distribution mechanisms
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import aiosqlite
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class Participant:
    """Real participant in the liberation system"""
    id: Optional[int] = None
    name: str = ""
    email: str = ""
    wallet_address: str = ""
    total_received: float = 0.0
    last_distribution: Optional[datetime] = None
    created_at: Optional[datetime] = None
    
    def to_dict(self):
        return asdict(self)

@dataclass
class Distribution:
    """Real distribution transaction"""
    id: Optional[int] = None
    participant_id: int = 0
    amount: float = 0.0
    type: str = "weekly_flow"  # weekly_flow, housing_credit, investment_pool
    transaction_hash: str = ""
    status: str = "pending"  # pending, processing, completed, failed
    created_at: Optional[datetime] = None

class RealityDistribution:
    """Real-world resource distribution system"""
    
    def __init__(self, db_path: str = "data/liberation_reality.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Configuration for real-world limits
        self.config = {
            "weekly_flow": 800.0,  # $800 per week
            "housing_credit": 104000.0,  # $104K housing credit
            "investment_pool": 104000.0,  # $104K investment access
            "max_participants": 1000,  # Start with 1000 people
            "test_mode": True,  # Start in test mode
            "min_age": 18,  # Minimum age requirement
            "verification_required": False,  # Trust by default
        }
        
        # Integration options for real money
        self.payment_integrations = {
            "stripe": False,  # Credit card payments
            "paypal": False,  # PayPal payments
            "crypto": False,  # Cryptocurrency
            "bank_transfer": False,  # Direct bank transfers
            "cash_app": False,  # Cash App
            "venmo": False,  # Venmo
            "test_mode": True,  # Test mode for development
        }
        
    async def initialize(self):
        """Initialize the distribution system"""
        logger.info("💰 Initializing Real-World Resource Distribution...")
        
        # Ensure database exists
        await self._create_database()
        
        # Load existing participants
        participants = await self.get_all_participants()
        logger.info(f"📊 Loaded {len(participants)} existing participants")
        
        # Show configuration
        logger.info("⚙️ Distribution Configuration:")
        logger.info(f"   Weekly Flow: ${self.config['weekly_flow']}")
        logger.info(f"   Housing Credit: ${self.config['housing_credit']}")
        logger.info(f"   Max Participants: {self.config['max_participants']}")
        logger.info(f"   Test Mode: {self.config['test_mode']}")
        
        return True
    
    async def _create_database(self):
        """Create database tables"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS participants (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE,
                    wallet_address TEXT,
                    total_received REAL DEFAULT 0,
                    last_distribution DATE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS distributions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    participant_id INTEGER,
                    amount REAL,
                    type TEXT,
                    transaction_hash TEXT,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (participant_id) REFERENCES participants (id)
                )
            """)
            
            await db.commit()
    
    async def add_participant(self, name: str, email: str, wallet_address: str = "") -> int:
        """Add a new participant to the system"""
        try:
            # Check if participant already exists
            existing = await self.get_participant_by_email(email)
            if existing:
                logger.warning(f"⚠️ Participant with email {email} already exists")
                return existing.id
            
            # Check participant limit
            current_count = await self.get_participant_count()
            if current_count >= self.config['max_participants']:
                logger.warning(f"⚠️ Maximum participants reached ({self.config['max_participants']})")
                return None
            
            # Add new participant
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute(
                    "INSERT INTO participants (name, email, wallet_address) VALUES (?, ?, ?)",
                    (name, email, wallet_address)
                )
                participant_id = cursor.lastrowid
                await db.commit()
                
                logger.info(f"✅ Added participant: {name} ({email})")
                
                # Give initial credits
                await self._give_initial_credits(participant_id)
                
                return participant_id
                
        except Exception as e:
            logger.error(f"❌ Failed to add participant: {e}")
            return None
    
    async def _give_initial_credits(self, participant_id: int):
        """Give initial credits to new participant"""
        try:
            # Housing credit
            await self._create_distribution(
                participant_id, 
                self.config['housing_credit'], 
                "housing_credit"
            )
            
            # Investment pool access
            await self._create_distribution(
                participant_id, 
                self.config['investment_pool'], 
                "investment_pool"
            )
            
            logger.info(f"💎 Initial credits given to participant {participant_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to give initial credits: {e}")
    
    async def _create_distribution(self, participant_id: int, amount: float, type: str):
        """Create a distribution record"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO distributions (participant_id, amount, type) VALUES (?, ?, ?)",
                (participant_id, amount, type)
            )
            await db.commit()
    
    async def weekly_distribution(self):
        """Perform weekly distribution to all participants"""
        logger.info("📅 Starting weekly distribution...")
        
        participants = await self.get_all_participants()
        total_distributed = 0.0
        successful_distributions = 0
        
        for participant in participants:
            try:
                # Check if already distributed this week
                if await self._already_distributed_this_week(participant.id):
                    logger.info(f"⏭️ Already distributed this week: {participant.name}")
                    continue
                
                # Create distribution
                distribution_id = await self._create_weekly_distribution(participant.id)
                
                if distribution_id:
                    # Process payment (in test mode, just mark as completed)
                    if self.config['test_mode']:
                        await self._complete_test_distribution(distribution_id)
                    else:
                        await self._process_real_payment(distribution_id, participant)
                    
                    total_distributed += self.config['weekly_flow']
                    successful_distributions += 1
                    
                    logger.info(f"💰 Distributed ${self.config['weekly_flow']} to {participant.name}")
                
            except Exception as e:
                logger.error(f"❌ Failed to distribute to {participant.name}: {e}")
        
        logger.info(f"✅ Weekly distribution complete:")
        logger.info(f"   Total distributed: ${total_distributed}")
        logger.info(f"   Successful distributions: {successful_distributions}")
        logger.info(f"   Failed distributions: {len(participants) - successful_distributions}")
        
        return {
            "total_distributed": total_distributed,
            "successful_distributions": successful_distributions,
            "failed_distributions": len(participants) - successful_distributions
        }
    
    async def _already_distributed_this_week(self, participant_id: int) -> bool:
        """Check if participant already received this week's distribution"""
        week_start = datetime.now() - timedelta(days=7)
        
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT COUNT(*) FROM distributions WHERE participant_id = ? AND type = 'weekly_flow' AND created_at > ?",
                (participant_id, week_start.isoformat())
            )
            count = await cursor.fetchone()
            return count[0] > 0
    
    async def _create_weekly_distribution(self, participant_id: int) -> int:
        """Create a weekly distribution record"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "INSERT INTO distributions (participant_id, amount, type) VALUES (?, ?, ?)",
                (participant_id, self.config['weekly_flow'], "weekly_flow")
            )
            await db.commit()
            return cursor.lastrowid
    
    async def _complete_test_distribution(self, distribution_id: int):
        """Complete a test distribution (no real money)"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE distributions SET status = 'completed', transaction_hash = ? WHERE id = ?",
                (f"test_tx_{distribution_id}", distribution_id)
            )
            await db.commit()
    
    async def _process_real_payment(self, distribution_id: int, participant: Participant):
        """Process real payment (placeholder for actual payment integration)"""
        # This would integrate with real payment systems
        logger.info(f"🔄 Processing real payment for {participant.name}")
        
        # Placeholder for payment processing
        # Could integrate with:
        # - Stripe for credit card payments
        # - PayPal API
        # - Cryptocurrency wallets
        # - Bank transfer APIs
        # - Cash App API
        # - Venmo API
        
        pass
    
    async def get_all_participants(self) -> List[Participant]:
        """Get all participants"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT id, name, email, wallet_address, total_received, last_distribution, created_at FROM participants"
            )
            rows = await cursor.fetchall()
            
            participants = []
            for row in rows:
                participants.append(Participant(
                    id=row[0],
                    name=row[1],
                    email=row[2],
                    wallet_address=row[3],
                    total_received=row[4],
                    last_distribution=row[5],
                    created_at=row[6]
                ))
            
            return participants
    
    async def get_participant_by_email(self, email: str) -> Optional[Participant]:
        """Get participant by email"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT id, name, email, wallet_address, total_received, last_distribution, created_at FROM participants WHERE email = ?",
                (email,)
            )
            row = await cursor.fetchone()
            
            if row:
                return Participant(
                    id=row[0],
                    name=row[1],
                    email=row[2],
                    wallet_address=row[3],
                    total_received=row[4],
                    last_distribution=row[5],
                    created_at=row[6]
                )
            return None
    
    async def get_participant_count(self) -> int:
        """Get total participant count"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT COUNT(*) FROM participants")
            count = await cursor.fetchone()
            return count[0]
    
    async def get_distribution_stats(self) -> Dict:
        """Get distribution statistics"""
        async with aiosqlite.connect(self.db_path) as db:
            # Total distributed
            cursor = await db.execute(
                "SELECT SUM(amount) FROM distributions WHERE status = 'completed'"
            )
            total_distributed = await cursor.fetchone()
            total_distributed = total_distributed[0] if total_distributed[0] else 0.0
            
            # Distribution count
            cursor = await db.execute(
                "SELECT COUNT(*) FROM distributions WHERE status = 'completed'"
            )
            distribution_count = await cursor.fetchone()
            distribution_count = distribution_count[0] if distribution_count[0] else 0
            
            # Participant count
            participant_count = await self.get_participant_count()
            
            return {
                "total_distributed": total_distributed,
                "distribution_count": distribution_count,
                "participant_count": participant_count,
                "weekly_flow": self.config['weekly_flow'],
                "housing_credit": self.config['housing_credit'],
                "test_mode": self.config['test_mode']
            }

async def main():
    """Test the reality distribution system"""
    system = RealityDistribution()
    await system.initialize()
    
    # Add some test participants
    await system.add_participant("Alice Johnson", "alice@example.com", "0x1234...")
    await system.add_participant("Bob Smith", "bob@example.com", "0x5678...")
    await system.add_participant("Carol Davis", "carol@example.com", "0x9abc...")
    
    # Show stats
    stats = await system.get_distribution_stats()
    print("📊 Distribution Stats:")
    print(f"   Participants: {stats['participant_count']}")
    print(f"   Total Distributed: ${stats['total_distributed']}")
    print(f"   Test Mode: {stats['test_mode']}")
    
    # Perform weekly distribution
    result = await system.weekly_distribution()
    print(f"\n💰 Weekly Distribution Results:")
    print(f"   Total Distributed: ${result['total_distributed']}")
    print(f"   Successful: {result['successful_distributions']}")

if __name__ == "__main__":
    asyncio.run(main())
