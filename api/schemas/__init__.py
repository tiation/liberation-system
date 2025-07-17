from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal

# Human schemas
class HumanRegistrationRequest(BaseModel):
    human_id: str = Field(..., description="Unique identifier for the human")
    name: Optional[str] = Field(None, description="Optional name")
    email: Optional[str] = Field(None, description="Optional email")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

class HumanResponse(BaseModel):
    id: str
    human_id: str
    weekly_flow: Decimal = Field(default=Decimal('800.00'))
    housing_credit: Decimal = Field(default=Decimal('104000.00'))
    investment_pool: Decimal = Field(default=Decimal('104000.00'))
    total_received: Decimal = Field(default=Decimal('0.00'))
    registration_date: datetime
    last_distribution: Optional[datetime] = None
    status: str = Field(default="active")

# Resource distribution schemas
class DistributionRequest(BaseModel):
    human_ids: Optional[List[str]] = Field(None, description="Specific humans to distribute to")
    amount_override: Optional[Decimal] = Field(None, description="Override default amount")
    distribution_type: str = Field(default="weekly", description="Type of distribution")

class DistributionResponse(BaseModel):
    success: bool
    recipients: int
    total_distributed: Decimal
    remaining_pool: Decimal
    distribution_id: str
    timestamp: datetime

# Truth spreading schemas
class TruthMessageRequest(BaseModel):
    content: str = Field(..., description="Truth message content")
    source: str = Field(..., description="Source of the truth")
    priority: int = Field(default=1, description="Priority level (1-5)")
    target_channels: Optional[List[str]] = Field(None, description="Specific channels to target")

class TruthMessageResponse(BaseModel):
    id: str
    content: str
    source: str
    priority: int
    created_at: datetime
    spread_count: int = Field(default=0)
    effectiveness_score: Decimal = Field(default=Decimal('0.00'))

class TruthSpreadResponse(BaseModel):
    message_id: str
    channels_reached: int
    total_reach: int
    effectiveness: Decimal
    timestamp: datetime

# Mesh network schemas
class MeshNodeRequest(BaseModel):
    node_id: str = Field(..., description="Unique node identifier")
    address: str = Field(..., description="Node network address")
    port: int = Field(..., description="Node port")
    public_key: Optional[str] = Field(None, description="Node public key")

class MeshNodeResponse(BaseModel):
    id: str
    node_id: str
    address: str
    port: int
    status: str = Field(default="active")
    last_seen: datetime
    transmission_power: Decimal = Field(default=Decimal('1.00'))
    connections_count: int = Field(default=0)

# System status schemas
class SystemStatusResponse(BaseModel):
    total_pool: Decimal
    distributed_today: Decimal
    active_humans: int
    active_communities: int
    mesh_nodes: int
    system_health: str
    uptime: str
    version: str = Field(default="1.0.0")

class SystemMetricsResponse(BaseModel):
    resource_distribution: Dict[str, Any]
    truth_spreading: Dict[str, Any]
    mesh_network: Dict[str, Any]
    performance: Dict[str, Any]

# Community schemas
class CommunityRequest(BaseModel):
    name: str = Field(..., description="Community name")
    member_count: int = Field(..., description="Number of members")
    governance_type: str = Field(default="democratic", description="Governance model")

class CommunityResponse(BaseModel):
    id: str
    name: str
    member_count: int
    total_pool_amount: Decimal
    housing_allocation: Decimal
    investment_allocation: Decimal
    community_projects: Decimal
    governance_type: str
    created_at: datetime
    status: str = Field(default="active")

# Housing allocation schemas
class HousingAllocationRequest(BaseModel):
    human_id: str = Field(..., description="Human requesting housing credit")
    amount: Decimal = Field(..., description="Amount requested")
    purpose: str = Field(..., description="Purpose of housing credit")

class HousingAllocationResponse(BaseModel):
    id: str
    human_id: str
    amount: Decimal
    community_id: str
    approved_date: datetime
    status: str = Field(default="approved")

# Error response schema
class ErrorResponse(BaseModel):
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)

# Success response schema
class SuccessResponse(BaseModel):
    success: bool = Field(default=True)
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)
