from pydantic import BaseModel
from datetime import datetime

class RequestRead(BaseModel):
    id: int
    requester_id: int
    approver_id: int
    breakglass_account_id: int
    status: str
    reason: str | None
    created_at: datetime
    approved_at: datetime | None
    rejected_at: datetime | None

    class Config:
        from_attributes = True
