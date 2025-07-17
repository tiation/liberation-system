from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
import aiosqlite
from datetime import datetime
from decimal import Decimal
import json
import uuid

from ..schemas import (
    HumanRegistrationRequest, 
    HumanResponse,
    DistributionRequest,
    DistributionResponse,
    CommunityRequest,
    CommunityResponse,
    HousingAllocationRequest,
    HousingAllocationResponse,
    SuccessResponse,
    ErrorResponse
)
from ..dependencies import (
    get_database, 
    get_current_user, 
    verify_human_exists,
    get_human_by_id,
    resource_pool
)
from ...realtime.events.system import event_system, EventType

router = APIRouter()

@router.post("/humans/register", response_model=HumanResponse)
async def register_human(
    request: HumanRegistrationRequest,
    db: aiosqlite.Connection = Depends(get_database),
    current_user: dict = Depends(get_current_user)
):
    """Register a new human in the liberation system"""
    try:
        # Check if human already exists
        if await verify_human_exists(request.human_id, db):
            raise HTTPException(
                status_code=400,
                detail=f"Human with ID {request.human_id} already registered"
            )
        
        # Register the human
        await db.execute(
            """INSERT INTO humans (human_identifier, weekly_flow, housing_credit, investment_pool, metadata) 
               VALUES (?, ?, ?, ?, ?)""",
            (
                request.human_id,
                800.00,
                104000.00,
                104000.00,
                json.dumps(request.metadata) if request.metadata else None
            )
        )
        await db.commit()
        
        # Return the registered human
        human = await get_human_by_id(request.human_id, db)
        
        # Publish human registration event
        await event_system.publish(
            event_type=EventType.HUMAN_REGISTERED,
            data={
                "human_id": request.human_id,
                "weekly_flow": float(human["weekly_flow"]),
                "housing_credit": float(human["housing_credit"]),
                "investment_pool": float(human["investment_pool"]),
                "method": "api_registration"
            },
            source="resources_api"
        )
        
        return HumanResponse(
            id=str(human["id"]),
            human_id=human["human_id"],
            weekly_flow=Decimal(str(human["weekly_flow"])),
            housing_credit=Decimal(str(human["housing_credit"])),
            investment_pool=Decimal(str(human["investment_pool"])),
            total_received=Decimal(str(human["total_received"])),
            registration_date=datetime.fromisoformat(human["registration_date"]),
            last_distribution=datetime.fromisoformat(human["last_distribution"]) if human["last_distribution"] else None,
            status=human["status"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to register human: {str(e)}"
        )

@router.get("/humans/{human_id}", response_model=HumanResponse)
async def get_human(
    human_id: str,
    db: aiosqlite.Connection = Depends(get_database),
    current_user: dict = Depends(get_current_user)
):
    """Get human information by ID"""
    human = await get_human_by_id(human_id, db)
    
    if not human:
        raise HTTPException(
            status_code=404,
            detail=f"Human with ID {human_id} not found"
        )
    
    return HumanResponse(
        id=str(human["id"]),
        human_id=human["human_id"],
        weekly_flow=Decimal(str(human["weekly_flow"])),
        housing_credit=Decimal(str(human["housing_credit"])),
        investment_pool=Decimal(str(human["investment_pool"])),
        total_received=Decimal(str(human["total_received"])),
        registration_date=datetime.fromisoformat(human["registration_date"]),
        last_distribution=datetime.fromisoformat(human["last_distribution"]) if human["last_distribution"] else None,
        status=human["status"]
    )

@router.get("/humans", response_model=List[HumanResponse])
async def list_humans(
    limit: int = 100,
    offset: int = 0,
    status: Optional[str] = None,
    db: aiosqlite.Connection = Depends(get_database),
    current_user: dict = Depends(get_current_user)
):
    """List all registered humans"""
    query = "SELECT * FROM humans"
    params = []
    
    if status:
        query += " WHERE status = ?"
        params.append(status)
    
    query += " LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    
    async with db.execute(query, params) as cursor:
        rows = await cursor.fetchall()
        
        humans = []
        for row in rows:
            humans.append(HumanResponse(
                id=str(row[0]),
                human_id=row[1],
                weekly_flow=Decimal(str(row[2])),
                housing_credit=Decimal(str(row[3])),
                investment_pool=Decimal(str(row[4])),
                total_received=Decimal(str(row[7])),
                registration_date=datetime.fromisoformat(row[5]),
                last_distribution=datetime.fromisoformat(row[6]) if row[6] else None,
                status=row[8]
            ))
        
        return humans

@router.post("/distribute", response_model=DistributionResponse)
async def distribute_resources(
    request: DistributionRequest,
    db: aiosqlite.Connection = Depends(get_database),
    current_user: dict = Depends(get_current_user)
):
    """Distribute resources to humans"""
    try:
        # Get humans to distribute to
        if request.human_ids:
            # Distribute to specific humans
            humans_query = "SELECT * FROM humans WHERE human_identifier IN ({})".format(
                ','.join(['?' for _ in request.human_ids])
            )
            async with db.execute(humans_query, request.human_ids) as cursor:
                humans = await cursor.fetchall()
        else:
            # Distribute to all active humans
            async with db.execute("SELECT * FROM humans WHERE status = 'active'") as cursor:
                humans = await cursor.fetchall()
        
        if not humans:
            raise HTTPException(
                status_code=404,
                detail="No humans found for distribution"
            )
        
        # Calculate distribution amount
        amount_per_human = float(request.amount_override or resource_pool.weekly_rate)
        total_amount = amount_per_human * len(humans)
        
        # Check available balance
        available_balance = await resource_pool.get_available_balance(db)
        if total_amount > available_balance:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient funds. Need ${total_amount:,.2f} but only ${available_balance:,.2f} available"
            )
        
        # Execute distributions
        distribution_id = str(uuid.uuid4())
        successful_distributions = 0
        
        for human in humans:
            try:
                await resource_pool.record_distribution(db, human[1], amount_per_human)
                successful_distributions += 1
            except Exception as e:
                print(f"Failed to distribute to {human[1]}: {e}")
                continue
        
        return DistributionResponse(
            success=True,
            recipients=successful_distributions,
            total_distributed=Decimal(str(successful_distributions * amount_per_human)),
            remaining_pool=Decimal(str(await resource_pool.get_available_balance(db))),
            distribution_id=distribution_id,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Distribution failed: {str(e)}"
        )

@router.get("/pool/status")
async def get_pool_status(
    db: aiosqlite.Connection = Depends(get_database),
    current_user: dict = Depends(get_current_user)
):
    """Get resource pool status"""
    try:
        available_balance = await resource_pool.get_available_balance(db)
        distributed_total = resource_pool.total_pool - available_balance
        
        # Get active humans count
        async with db.execute("SELECT COUNT(*) FROM humans WHERE status = 'active'") as cursor:
            active_humans = await cursor.fetchone()
        
        # Get today's distributions
        async with db.execute(
            "SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE DATE(timestamp) = DATE('now')"
        ) as cursor:
            today_distributed = await cursor.fetchone()
        
        return {
            "total_pool": resource_pool.total_pool,
            "available_balance": available_balance,
            "distributed_total": distributed_total,
            "active_humans": active_humans[0],
            "today_distributed": today_distributed[0] or 0,
            "weekly_rate": resource_pool.weekly_rate
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get pool status: {str(e)}"
        )

@router.post("/communities", response_model=CommunityResponse)
async def create_community(
    request: CommunityRequest,
    db: aiosqlite.Connection = Depends(get_database),
    current_user: dict = Depends(get_current_user)
):
    """Create a new community abundance pool"""
    try:
        # Calculate community pool amounts
        total_pool_amount = request.member_count * 104000  # $104K per member
        housing_allocation = total_pool_amount * 0.5  # 50% for housing
        investment_allocation = total_pool_amount * 0.3  # 30% for investment
        community_projects = total_pool_amount * 0.2  # 20% for projects
        
        # Create community
        cursor = await db.execute(
            """INSERT INTO communities (name, member_count, total_pool_amount, housing_allocation, 
                                      investment_allocation, community_projects, governance_type) 
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                request.name,
                request.member_count,
                total_pool_amount,
                housing_allocation,
                investment_allocation,
                community_projects,
                request.governance_type
            )
        )
        await db.commit()
        
        community_id = cursor.lastrowid
        
        return CommunityResponse(
            id=str(community_id),
            name=request.name,
            member_count=request.member_count,
            total_pool_amount=Decimal(str(total_pool_amount)),
            housing_allocation=Decimal(str(housing_allocation)),
            investment_allocation=Decimal(str(investment_allocation)),
            community_projects=Decimal(str(community_projects)),
            governance_type=request.governance_type,
            created_at=datetime.now(),
            status="active"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create community: {str(e)}"
        )

@router.get("/communities", response_model=List[CommunityResponse])
async def list_communities(
    limit: int = 100,
    offset: int = 0,
    db: aiosqlite.Connection = Depends(get_database),
    current_user: dict = Depends(get_current_user)
):
    """List all communities"""
    try:
        async with db.execute(
            "SELECT * FROM communities ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (limit, offset)
        ) as cursor:
            rows = await cursor.fetchall()
            
            communities = []
            for row in rows:
                communities.append(CommunityResponse(
                    id=str(row[0]),
                    name=row[1],
                    member_count=row[2],
                    total_pool_amount=Decimal(str(row[3])),
                    housing_allocation=Decimal(str(row[4])),
                    investment_allocation=Decimal(str(row[5])),
                    community_projects=Decimal(str(row[6])),
                    governance_type=row[7],
                    created_at=datetime.fromisoformat(row[8]),
                    status=row[9]
                ))
            
            return communities
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list communities: {str(e)}"
        )

@router.post("/communities/{community_id}/housing", response_model=HousingAllocationResponse)
async def allocate_housing_credit(
    community_id: str,
    request: HousingAllocationRequest,
    db: aiosqlite.Connection = Depends(get_database),
    current_user: dict = Depends(get_current_user)
):
    """Allocate housing credit to a community member"""
    try:
        # Verify community exists and has sufficient funds
        async with db.execute(
            "SELECT housing_allocation FROM communities WHERE id = ?",
            (community_id,)
        ) as cursor:
            community = await cursor.fetchone()
            
        if not community:
            raise HTTPException(
                status_code=404,
                detail=f"Community {community_id} not found"
            )
        
        available_housing = community[0]
        if float(request.amount) > available_housing:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient housing funds. Available: ${available_housing:,.2f}, Requested: ${request.amount:,.2f}"
            )
        
        # Verify human exists
        if not await verify_human_exists(request.human_id, db):
            raise HTTPException(
                status_code=404,
                detail=f"Human {request.human_id} not found"
            )
        
        # Allocate housing credit
        allocation_id = str(uuid.uuid4())
        
        # Update community housing allocation
        await db.execute(
            "UPDATE communities SET housing_allocation = housing_allocation - ? WHERE id = ?",
            (float(request.amount), community_id)
        )
        
        # Record transaction
        await db.execute(
            """INSERT INTO transactions (human_id, amount, transaction_type, metadata) 
               VALUES (?, ?, ?, ?)""",
            (
                request.human_id,
                float(request.amount),
                "housing_credit",
                json.dumps({
                    "allocation_id": allocation_id,
                    "community_id": community_id,
                    "purpose": request.purpose
                })
            )
        )
        await db.commit()
        
        return HousingAllocationResponse(
            id=allocation_id,
            human_id=request.human_id,
            amount=request.amount,
            community_id=community_id,
            approved_date=datetime.now(),
            status="approved"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to allocate housing credit: {str(e)}"
        )
