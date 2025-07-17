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
from ...core.database_optimization import get_optimized_database_manager

router = APIRouter()

@router.post("/humans/register", response_model=HumanResponse)
async def register_human(
    request: HumanRegistrationRequest,
    db: aiosqlite.Connection = Depends(get_database)
):
    """Register a new human in the liberation system with cache invalidation - Trust-by-default: No authentication required"""
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
        
        # Get the registered human
        human = await get_human_by_id(request.human_id, db)
        
        # Invalidate relevant caches
        optimized_db = await get_optimized_database_manager()
        await optimized_db.invalidate_cache("human_stats*")
        await optimized_db.invalidate_cache("transaction_summary*")
        
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
    db: aiosqlite.Connection = Depends(get_database)
):
    """Get human information by ID with caching - Trust-by-default: Open access"""
    try:
        # Try to get from cache first
        optimized_db = await get_optimized_database_manager()
        cache_key = f"human_{human_id}"
        cached_human = await optimized_db.cache_manager.get(cache_key)
        
        if cached_human:
            return HumanResponse(**cached_human)
        
        # If not in cache, query database
        human = await get_human_by_id(human_id, db)
        
        if not human:
            raise HTTPException(
                status_code=404,
                detail=f"Human with ID {human_id} not found"
            )
        
        response = HumanResponse(
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
        
        # Cache the result for 10 minutes
        await optimized_db.cache_manager.set(cache_key, response.dict(), ttl=600)
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get human: {str(e)}"
        )

@router.get("/humans", response_model=List[HumanResponse])
async def list_humans(
    limit: int = 100,
    offset: int = 0,
    status: Optional[str] = None,
    db: aiosqlite.Connection = Depends(get_database)
):
    """List all registered humans with optimized query and caching - Trust-by-default: Open access"""
    try:
        # Create cache key based on parameters
        cache_key = f"humans_list_{limit}_{offset}_{status or 'all'}"
        
        # Try to get from cache first
        optimized_db = await get_optimized_database_manager()
        cached_humans = await optimized_db.cache_manager.get(cache_key)
        
        if cached_humans:
            return [HumanResponse(**human) for human in cached_humans]
        
        # Build optimized query using indexes
        if status:
            # Use the status index
            query = """
                SELECT * FROM humans 
                WHERE status = ? 
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """
            params = [status, limit, offset]
        else:
            query = """
                SELECT * FROM humans 
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """
            params = [limit, offset]
        
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
            
            # Cache the result for 5 minutes
            humans_dict = [human.dict() for human in humans]
            await optimized_db.cache_manager.set(cache_key, humans_dict, ttl=300)
            
            return humans
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list humans: {str(e)}"
        )

@router.post("/distribute", response_model=DistributionResponse)
async def distribute_resources(
    request: DistributionRequest,
    db: aiosqlite.Connection = Depends(get_database),
    current_user: dict = Depends(get_current_user)
):
    """Distribute resources to humans with cache invalidation"""
    try:
        # Get humans to distribute to using optimized query
        if request.human_ids:
            # Use the human_id index for targeted distribution
            placeholders = ','.join(['?' for _ in request.human_ids])
            humans_query = f"""
                SELECT * FROM humans 
                WHERE human_identifier IN ({placeholders})
                AND status = 'active'
            """
            async with db.execute(humans_query, request.human_ids) as cursor:
                humans = await cursor.fetchall()
        else:
            # Use the status index for bulk distribution
            async with db.execute("""
                SELECT * FROM humans 
                WHERE status = 'active'
                ORDER BY last_distribution ASC NULLS FIRST
            """) as cursor:
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
        
        # Execute distributions with batch processing
        distribution_id = str(uuid.uuid4())
        successful_distributions = 0
        
        # Batch insert for better performance
        batch_updates = []
        batch_transactions = []
        
        for human in humans:
            try:
                # Prepare batch updates
                batch_updates.append((
                    float(human[7]) + amount_per_human,  # total_received
                    datetime.now().isoformat(),  # last_distribution
                    human[0]  # id
                ))
                
                # Prepare batch transactions
                batch_transactions.append((
                    human[1],  # human_id
                    amount_per_human,  # amount
                    request.distribution_type,  # transaction_type
                    datetime.now().isoformat(),  # timestamp
                    'completed'  # status
                ))
                
                successful_distributions += 1
                
            except Exception as e:
                print(f"Failed to prepare distribution for {human[1]}: {e}")
                continue
        
        # Execute batch updates
        await db.executemany(
            "UPDATE humans SET total_received = ?, last_distribution = ? WHERE id = ?",
            batch_updates
        )
        
        await db.executemany(
            "INSERT INTO transactions (human_id, amount, transaction_type, timestamp, status) VALUES (?, ?, ?, ?, ?)",
            batch_transactions
        )
        
        await db.commit()
        
        # Invalidate relevant caches
        optimized_db = await get_optimized_database_manager()
        await optimized_db.invalidate_cache("human_stats*")
        await optimized_db.invalidate_cache("transaction_summary*")
        await optimized_db.invalidate_cache("humans_list*")
        
        # Publish distribution event
        await event_system.publish(
            event_type=EventType.RESOURCE_DISTRIBUTED,
            data={
                "distribution_id": distribution_id,
                "recipients": successful_distributions,
                "total_amount": successful_distributions * amount_per_human,
                "distribution_type": request.distribution_type
            },
            source="resources_api"
        )
        
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
    """Get resource pool status with cached statistics"""
    try:
        # Get cached statistics from optimized database
        optimized_db = await get_optimized_database_manager()
        
        # Get human stats from cache/materialized view
        human_stats = await optimized_db.get_human_stats()
        
        # Get transaction summary from cache/materialized view
        transaction_summary = await optimized_db.get_transaction_summary(days=1)
        
        # Calculate today's distributed amount
        today_distributed = 0
        for summary in transaction_summary:
            if summary.get('transaction_date') and summary.get('transaction_date').date() == datetime.now().date():
                today_distributed += float(summary.get('total_amount', 0))
        
        available_balance = await resource_pool.get_available_balance(db)
        
        return {
            "total_pool": resource_pool.total_pool,
            "available_balance": available_balance,
            "distributed_total": float(human_stats.get('total_distributed', 0)),
            "active_humans": human_stats.get('active_humans', 0),
            "total_humans": human_stats.get('total_humans', 0),
            "today_distributed": today_distributed,
            "weekly_rate": resource_pool.weekly_rate,
            "recent_distributions": human_stats.get('recent_distributions', 0),
            "last_distribution_date": str(human_stats.get('last_distribution_date', ''))
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get pool status: {str(e)}"
        )

@router.get("/stats/summary")
async def get_system_summary(
    current_user: dict = Depends(get_current_user)
):
    """Get comprehensive system statistics with caching"""
    try:
        optimized_db = await get_optimized_database_manager()
        
        # Get all cached statistics
        human_stats = await optimized_db.get_human_stats()
        transaction_summary = await optimized_db.get_transaction_summary(days=30)
        knowledge_stats = await optimized_db.get_knowledge_stats()
        mesh_health = await optimized_db.get_mesh_health()
        
        return {
            "human_statistics": human_stats,
            "transaction_summary": transaction_summary,
            "knowledge_statistics": knowledge_stats,
            "mesh_network_health": mesh_health,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get system summary: {str(e)}"
        )

@router.post("/cache/invalidate")
async def invalidate_cache(
    pattern: str,
    current_user: dict = Depends(get_current_user)
):
    """Manually invalidate cache entries (admin only)"""
    try:
        optimized_db = await get_optimized_database_manager()
        await optimized_db.invalidate_cache(pattern)
        
        return {
            "success": True,
            "message": f"Cache invalidated for pattern: {pattern}",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to invalidate cache: {str(e)}"
        )

@router.get("/performance/metrics")
async def get_performance_metrics(
    current_user: dict = Depends(get_current_user)
):
    """Get database performance metrics"""
    try:
        optimized_db = await get_optimized_database_manager()
        
        # Get cache statistics
        cache_stats = {
            "local_cache_size": len(optimized_db.cache_manager.local_cache),
            "redis_available": optimized_db.cache_manager.redis_client is not None
        }
        
        # Get database statistics (if available)
        db_stats = {}
        try:
            # Query for database size and performance metrics
            db_size_query = """
                SELECT 
                    pg_size_pretty(pg_database_size(current_database())) as database_size,
                    (SELECT count(*) FROM humans) as humans_count,
                    (SELECT count(*) FROM transactions) as transactions_count,
                    (SELECT count(*) FROM knowledge_entries) as knowledge_count
            """
            db_result = await optimized_db.db_manager.fetch_one(db_size_query)
            if db_result:
                db_stats = dict(db_result)
        except Exception as e:
            db_stats = {"error": str(e)}
        
        return {
            "cache_statistics": cache_stats,
            "database_statistics": db_stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get performance metrics: {str(e)}"
        )
