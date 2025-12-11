from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class DiscoveryResponse(BaseModel):
    id: int
    file_metadata: Dict
    storage_path: str
    storage_type: str
    environment: Optional[str]
    data_source_type: Optional[str]
    status: str
    discovered_at: datetime
    
    class Config:
        from_attributes = True


class DiscoveryListResponse(BaseModel):
    discoveries: List[Dict[str, Any]]
    pagination: Dict[str, Any]


class ApproveRequest(BaseModel):
    approved_by: str = Field(..., description="Email/username of approver")
    role: Optional[str] = Field(None, description="Role of approver")
    comments: Optional[str] = Field(None, description="Approval comments")


class RejectRequest(BaseModel):
    rejected_by: str = Field(..., description="Email/username of rejector")
    rejection_reason: Optional[str] = Field(None, description="Reason for rejection")
    role: Optional[str] = Field(None, description="Role of rejector")
    comments: Optional[str] = Field(None, description="Rejection comments")


class SummaryStatsResponse(BaseModel):
    total_discoveries: int
    pending_count: int
    approved_count: int
    rejected_count: int
