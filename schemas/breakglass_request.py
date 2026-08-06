from pydantic import BaseModel
from datetime import datetime

class BreakglassRequestCreate(BaseModel):
    device_id: int
    reason: str

class BreakglassRequestRead(BaseModel):
    id: int
    requester_id: int
    approver_id: int | None
    device_id: int
    reason: str
    status: str
    otp_verified: bool
    created_at: datetime
    approved_at: datetime | None

    class Config:
        from_attributes = True
