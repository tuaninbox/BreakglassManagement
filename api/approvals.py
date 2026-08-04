from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import get_db
from deps.auth import get_current_user
from core.logging import log_event
from core.otp import verify_otp
from models.request import AccessRequest
from models.user import User

router = APIRouter(prefix="/api/approvals", tags=["approvals"])

@router.post("/{request_id}/approve-otp")
async def approve_with_otp(
    request_id: int,
    otp_code: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    req = await db.get(AccessRequest, request_id)
    if not req or req.status != "pending":
        raise HTTPException(status_code=404, detail="Request not found or not pending")

    if current_user.id != req.approver_id:
        raise HTTPException(status_code=403, detail="Not the approver for this request")

    if req.requester_id == current_user.id:
        raise HTTPException(status_code=403, detail="Cannot approve own request")

    if not current_user.otp_secret or not verify_otp(current_user.otp_secret, otp_code):
        raise HTTPException(status_code=400, detail="Invalid OTP")

    req.status = "approved"
    req.approval_channel = "otp_code"
    req.approved_at = datetime.utcnow()
    req.session_expires_at = datetime.utcnow() + timedelta(minutes=30)
    await db.commit()
    await db.refresh(req)

    log_event("REQUEST_APPROVED_OTP", request_id=req.id, approver=current_user.username)
    return {"id": req.id, "status": req.status}
