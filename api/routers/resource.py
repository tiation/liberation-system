from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime
import sys
import os
import importlib.util

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import Liberation System core
from core.resource_distribution import SystemCore
from security.trust_default import AntiSecurity
from api.models.schemas import (
    HumanCreate, HumanResponse, DistributionRequest, DistributionResponse,
    SystemStats, SecurityRequest, SecurityResponse, ApiResponse, ErrorResponse
)

router = APIRouter()

# Global system instance
system_core = None
security_system = None

async def get_system_core():
    """Get or create system core instance"""
    global system_core
    if system_core is None:
        system_core = SystemCore()
        await system_core.initialize()
    return system_core

async def get_security_system():
    """Get or create security system instance"""
    global security_system
    if security_system is None:
        security_system = AntiSecurity()
    return security_system

# Human Management Endpoints

@router.post("/humans", response_model=ApiResponse, tags=["humans"])
async def create_human(
    human: HumanCreate,
    system: SystemCore = Depends(get_system_core)
):
    """Create a new human in the system"""
    try:
        success = await system.add_human(human.id)
        if success:
            return ApiResponse(
                success=True,
                message=f"Human {human.id} created successfully",
                data={"human_id": human.id}
            )
        else:
            return ApiResponse(
                success=False,
                message=f"Human {human.id} already exists or creation failed"
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/humans", response_model=List[HumanResponse], tags=["humans"])
async def get_all_humans(
    system: SystemCore = Depends(get_system_core)
):
    """Get all humans in the system"""
    try:
        humans = []
        for human in system.resource_pool.humans.values():
            humans.append(HumanResponse(
                id=human.id,
                weekly_flow=human.weekly_flow,
                housing_credit=human.housing_credit,
                investment_pool=human.investment_pool,
                status=human.status,
                created_at=human.created_at,
                last_distribution=human.last_distribution,
                total_received=human.total_received
            ))
        return humans
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/humans/{human_id}", response_model=HumanResponse, tags=["humans"])
async def get_human(
    human_id: str,
    system: SystemCore = Depends(get_system_core)
):
    """Get a specific human by ID"""
    try:
        if human_id not in system.resource_pool.humans:
            raise HTTPException(status_code=404, detail="Human not found")
        
        human = system.resource_pool.humans[human_id]
        return HumanResponse(
            id=human.id,
            weekly_flow=human.weekly_flow,
            housing_credit=human.housing_credit,
            investment_pool=human.investment_pool,
            status=human.status,
            created_at=human.created_at,
            last_distribution=human.last_distribution,
            total_received=human.total_received
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/humans/{human_id}", response_model=ApiResponse, tags=["humans"])
async def delete_human(
    human_id: str,
    system: SystemCore = Depends(get_system_core)
):
    """Remove a human from the system"""
    try:
        if human_id not in system.resource_pool.humans:
            raise HTTPException(status_code=404, detail="Human not found")
        
        # Set human status to inactive instead of deleting
        human = system.resource_pool.humans[human_id]
        human.status = "inactive"
        await system.resource_pool._save_human(human)
        
        return ApiResponse(
            success=True,
            message=f"Human {human_id} deactivated successfully",
            data={"human_id": human_id, "status": "inactive"}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Distribution Endpoints

@router.post("/distribute", response_model=DistributionResponse, tags=["distribution"])
async def distribute_resources(
    request: Optional[DistributionRequest] = None,
    system: SystemCore = Depends(get_system_core)
):
    """Distribute resources to humans"""
    try:
        if request is None:
            request = DistributionRequest()
        
        # If specific human IDs are provided, distribute only to them
        if request.human_ids:
            # Filter humans
            original_humans = system.resource_pool.humans.copy()
            system.resource_pool.humans = {
                hid: human for hid, human in original_humans.items() 
                if hid in request.human_ids
            }
        
        # Override amount if specified
        if request.amount_override:
            for human in system.resource_pool.humans.values():
                human.weekly_flow = request.amount_override
        
        # Perform distribution
        await system.resource_pool.distribute_weekly()
        
        # Get statistics
        stats = await system.get_system_stats()
        
        # Restore original humans if filtered
        if request.human_ids:
            system.resource_pool.humans = original_humans
        
        return DistributionResponse(
            success=True,
            total_distributed=stats['distributed_this_week'],
            humans_count=len(request.human_ids) if request.human_ids else stats['total_humans'],
            errors=None,
            timestamp=datetime.now()
        )
    except Exception as e:
        return DistributionResponse(
            success=False,
            total_distributed=0,
            humans_count=0,
            errors=[str(e)],
            timestamp=datetime.now()
        )

@router.get("/stats", response_model=SystemStats, tags=["system"])
async def get_system_stats(
    system: SystemCore = Depends(get_system_core)
):
    """Get system statistics"""
    try:
        stats = await system.get_system_stats()
        return SystemStats(
            total_humans=stats['total_humans'],
            active_humans=stats['active_humans'],
            total_distributed=stats['total_distributed'],
            distributed_this_week=stats['distributed_this_week'],
            remaining_wealth=stats['remaining_wealth'],
            average_per_human=stats['average_per_human'],
            uptime=stats.get('uptime', 0)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Security Endpoints

@router.post("/security/check", response_model=SecurityResponse, tags=["security"])
async def check_access(
    request: SecurityRequest,
    security: AntiSecurity = Depends(get_security_system)
):
    """Check access permissions"""
    try:
        response = security.process_request({
            "human_id": request.human_id,
            "resource_id": request.resource_id,
            "action": request.action
        })
        
        return SecurityResponse(
            access=response['access'],
            message=response['message'],
            timestamp=datetime.now()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Automation Endpoints

@router.get("/automation/stats", response_model=dict, tags=["automation"])
async def get_automation_stats():
    """Get automation system statistics"""
    try:
        # Import automation system
        spec = importlib.util.spec_from_file_location("automation_system", "core/automation-system.py")
        automation_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(automation_module)
        
        # Create manager instance
        manager = automation_module.SystemManager()
        await manager.initialize()
        await manager.setup_all_systems()
        
        # Get stats
        stats = await manager.automation.get_task_statistics()
        
        return {
            "success": True,
            "data": stats,
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/automation/run-task/{task_name}", response_model=ApiResponse, tags=["automation"])
async def run_automation_task(task_name: str):
    """Run a specific automation task"""
    try:
        # Import automation system
        spec = importlib.util.spec_from_file_location("automation_system", "core/automation-system.py")
        automation_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(automation_module)
        
        # Create manager instance
        manager = automation_module.SystemManager()
        await manager.initialize()
        await manager.setup_all_systems()
        
        # Run specific task
        if task_name in manager.automation.tasks:
            task = manager.automation.tasks[task_name]
            await manager.automation._run_task(task)
            
            return ApiResponse(
                success=True,
                message=f"Task {task_name} executed successfully",
                data={"task_name": task_name, "status": task.status}
            )
        else:
            raise HTTPException(status_code=404, detail=f"Task {task_name} not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Utility Endpoints

@router.get("/health", response_model=dict, tags=["system"])
async def health_check():
    """Check system health"""
    try:
        system = await get_system_core()
        stats = await system.get_system_stats()
        
        return {
            "status": "healthy",
            "message": "Liberation System is operational",
            "humans_count": stats['total_humans'],
            "total_distributed": float(stats['total_distributed']),
            "timestamp": datetime.now()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": f"System error: {str(e)}",
            "timestamp": datetime.now()
        }
