"""
Liberation System - Resource Management Module
Handles resource allocation, distribution, and flow management.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import json


@dataclass
class ResourcePool:
    """Resource pool data structure"""
    total_resources: int = 19_000_000_000_000  # 19 trillion
    available_resources: int = 19_000_000_000_000
    allocated_resources: int = 0
    weekly_flow_rate: int = 800
    last_distribution: Optional[datetime] = None
    

@dataclass
class ResourceAllocation:
    """Resource allocation record"""
    recipient_id: str
    amount: int
    timestamp: datetime
    purpose: str
    status: str = "pending"
    

class ResourceManager:
    """Manages resource distribution and allocation"""
    
    def __init__(self):
        self.pool = ResourcePool()
        self.allocations: List[ResourceAllocation] = []
        self.distribution_history: List[Dict[str, Any]] = []
        self.logger = logging.getLogger(__name__)
        
    async def initialize(self):
        """Initialize the resource management system"""
        self.logger.info("🔄 Initializing Resource Management System")
        
        # Reset to default state
        self.pool = ResourcePool()
        self.pool.last_distribution = datetime.now()
        
        self.logger.info(f"💰 Resource Pool initialized with {self.pool.total_resources:,} total resources")
        self.logger.info(f"⚡ Weekly flow rate: {self.pool.weekly_flow_rate}")
        
    async def allocate_resources(self, recipient_id: str, amount: int, purpose: str = "general") -> bool:
        """Allocate resources to a recipient"""
        try:
            if amount <= 0:
                self.logger.error(f"❌ Invalid allocation amount: {amount}")
                return False
                
            if amount > self.pool.available_resources:
                self.logger.warning(f"⚠️ Insufficient resources. Requested: {amount:,}, Available: {self.pool.available_resources:,}")
                return False
                
            # Create allocation record
            allocation = ResourceAllocation(
                recipient_id=recipient_id,
                amount=amount,
                timestamp=datetime.now(),
                purpose=purpose,
                status="completed"
            )
            
            # Update pool
            self.pool.available_resources -= amount
            self.pool.allocated_resources += amount
            
            # Record allocation
            self.allocations.append(allocation)
            
            self.logger.info(f"✅ Allocated {amount:,} resources to {recipient_id} for {purpose}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error allocating resources: {e}")
            return False
            
    async def distribute_weekly_flow(self) -> Dict[str, Any]:
        """Distribute weekly resource flow"""
        try:
            now = datetime.now()
            
            # Check if it's time for distribution
            if self.pool.last_distribution:
                time_since_last = now - self.pool.last_distribution
                if time_since_last < timedelta(weeks=1):
                    remaining_time = timedelta(weeks=1) - time_since_last
                    return {
                        "status": "pending",
                        "message": f"Next distribution in {remaining_time}",
                        "amount": 0
                    }
            
            # Distribute resources
            flow_amount = self.pool.weekly_flow_rate
            
            # Add to available resources
            self.pool.available_resources += flow_amount
            self.pool.last_distribution = now
            
            # Record distribution
            distribution_record = {
                "timestamp": now.isoformat(),
                "amount": flow_amount,
                "total_available": self.pool.available_resources,
                "total_allocated": self.pool.allocated_resources
            }
            
            self.distribution_history.append(distribution_record)
            
            self.logger.info(f"📈 Weekly flow distributed: {flow_amount:,} resources")
            
            return {
                "status": "completed",
                "message": f"Distributed {flow_amount:,} resources",
                "amount": flow_amount,
                "total_available": self.pool.available_resources
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error distributing weekly flow: {e}")
            return {
                "status": "error",
                "message": str(e),
                "amount": 0
            }
            
    async def get_pool_status(self) -> Dict[str, Any]:
        """Get current resource pool status"""
        return {
            "total_resources": self.pool.total_resources,
            "available_resources": self.pool.available_resources,
            "allocated_resources": self.pool.allocated_resources,
            "utilization_rate": (self.pool.allocated_resources / self.pool.total_resources) * 100,
            "weekly_flow_rate": self.pool.weekly_flow_rate,
            "last_distribution": self.pool.last_distribution.isoformat() if self.pool.last_distribution else None,
            "total_allocations": len(self.allocations)
        }
        
    async def get_allocation_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get allocation history"""
        return [
            {
                "recipient_id": alloc.recipient_id,
                "amount": alloc.amount,
                "timestamp": alloc.timestamp.isoformat(),
                "purpose": alloc.purpose,
                "status": alloc.status
            }
            for alloc in self.allocations[-limit:]
        ]
        
    async def get_distribution_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get distribution history"""
        return self.distribution_history[-limit:]
        
    async def emergency_resource_release(self, amount: int) -> bool:
        """Emergency resource release mechanism"""
        try:
            if amount <= 0:
                return False
                
            # Add resources to available pool
            self.pool.available_resources += amount
            
            # Record emergency release
            emergency_record = {
                "timestamp": datetime.now().isoformat(),
                "amount": amount,
                "type": "emergency_release",
                "total_available": self.pool.available_resources
            }
            
            self.distribution_history.append(emergency_record)
            
            self.logger.warning(f"🚨 Emergency resource release: {amount:,} resources")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error in emergency resource release: {e}")
            return False
            
    async def optimize_distribution(self) -> Dict[str, Any]:
        """Optimize resource distribution based on usage patterns"""
        try:
            # Analyze allocation patterns
            if not self.allocations:
                return {"status": "no_data", "message": "No allocation data available"}
                
            # Calculate metrics
            recent_allocations = [alloc for alloc in self.allocations 
                                if alloc.timestamp > datetime.now() - timedelta(days=7)]
            
            if not recent_allocations:
                return {"status": "no_recent_data", "message": "No recent allocations"}
                
            total_recent = sum(alloc.amount for alloc in recent_allocations)
            avg_allocation = total_recent / len(recent_allocations)
            
            # Optimization recommendations
            recommendations = []
            
            if avg_allocation > self.pool.weekly_flow_rate * 0.1:
                recommendations.append("Consider increasing weekly flow rate")
                
            if self.pool.available_resources < self.pool.total_resources * 0.1:
                recommendations.append("Resource pool running low, consider emergency release")
                
            utilization = (self.pool.allocated_resources / self.pool.total_resources) * 100
            if utilization > 80:
                recommendations.append("High resource utilization detected")
                
            return {
                "status": "completed",
                "metrics": {
                    "recent_allocations": len(recent_allocations),
                    "total_recent_amount": total_recent,
                    "average_allocation": avg_allocation,
                    "utilization_rate": utilization
                },
                "recommendations": recommendations
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error optimizing distribution: {e}")
            return {"status": "error", "message": str(e)}


# Global resource manager instance
resource_manager = ResourceManager()


async def initialize_resource_management():
    """Initialize the global resource manager"""
    await resource_manager.initialize()


async def main():
    """Main function for testing"""
    await initialize_resource_management()
    
    # Test allocation
    success = await resource_manager.allocate_resources("user123", 1000, "testing")
    print(f"Allocation successful: {success}")
    
    # Test status
    status = await resource_manager.get_pool_status()
    print(f"Pool status: {json.dumps(status, indent=2)}")
    
    # Test distribution
    distribution = await resource_manager.distribute_weekly_flow()
    print(f"Distribution: {json.dumps(distribution, indent=2)}")


if __name__ == "__main__":
    asyncio.run(main())
