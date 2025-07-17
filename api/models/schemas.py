from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class HumanBase(BaseModel):
    id: str = Field(..., description="Unique human identifier")
    weekly_flow: Optional[Decimal] = Field(default=Decimal('800.00'), description="Weekly resource flow amount")
    housing_credit: Optional[Decimal] = Field(default=Decimal('104000.00'), description="Housing credit amount")
    investment_pool: Optional[Decimal] = Field(default=Decimal('104000.00'), description="Investment pool amount")
    status: Optional[str] = Field(default="active", description="Human status")

class HumanCreate(HumanBase):
    pass

class HumanResponse(HumanBase):
    created_at: datetime = Field(..., description="Creation timestamp")
    last_distribution: Optional[datetime] = Field(None, description="Last distribution timestamp")
    total_received: Decimal = Field(..., description="Total amount received")
    
    class Config:
        from_attributes = True

class DistributionRequest(BaseModel):
    human_ids: Optional[List[str]] = Field(None, description="Specific human IDs to distribute to (optional)")
    amount_override: Optional[Decimal] = Field(None, description="Override default distribution amount")

class DistributionResponse(BaseModel):
    success: bool = Field(..., description="Distribution success status")
    total_distributed: Decimal = Field(..., description="Total amount distributed")
    humans_count: int = Field(..., description="Number of humans that received distribution")
    errors: Optional[List[str]] = Field(None, description="Any errors encountered")
    timestamp: datetime = Field(..., description="Distribution timestamp")

class SystemStats(BaseModel):
    total_humans: int = Field(..., description="Total number of humans in system")
    active_humans: int = Field(..., description="Number of active humans")
    total_distributed: Decimal = Field(..., description="Total amount distributed")
    distributed_this_week: Decimal = Field(..., description="Amount distributed this week")
    remaining_wealth: Decimal = Field(..., description="Remaining wealth in pool")
    average_per_human: Decimal = Field(..., description="Average amount per human")
    uptime: float = Field(..., description="System uptime in seconds")

class SecurityRequest(BaseModel):
    human_id: str = Field(..., description="Human ID requesting access")
    resource_id: str = Field(..., description="Resource ID being accessed")
    action: str = Field(..., description="Action being performed")

class SecurityResponse(BaseModel):
    access: bool = Field(..., description="Access granted status")
    message: str = Field(..., description="Access response message")
    timestamp: datetime = Field(..., description="Access check timestamp")

class TaskStats(BaseModel):
    total_tasks: int = Field(..., description="Total number of tasks")
    active_tasks: int = Field(..., description="Number of active tasks")
    total_runs: int = Field(..., description="Total task runs")
    success_rate: float = Field(..., description="Success rate percentage")
    average_duration: float = Field(..., description="Average task duration")
    uptime: float = Field(..., description="System uptime in seconds")

class ApiResponse(BaseModel):
    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Response message")
    data: Optional[dict] = Field(None, description="Response data")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")

class ErrorResponse(BaseModel):
    success: bool = Field(False, description="Operation success status")
    error: str = Field(..., description="Error message")
    code: int = Field(..., description="Error code")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")
