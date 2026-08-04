from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.db import get_db
from deps.auth import get_current_user
from core.logging import log_event
from core.email import send_email
from models.request import AccessRequest
from models.account import BreakglassAccount
from models.user import User

router = APIRouter(prefix="/api/requests", tags=["requests"])

@router.post("/", status_code=201)
async def create_request(
    account_id: int,
    reason: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in ("requester", "requester_approver"):
        raise HTTPException(status_code=403, detail="Not a requester")

    account = await db.get(BreakglassAccount, account_id)
    if not account or not account.is_enabled:
        raise HTTPException(status_code=404, detail="Account not found")

    stmt = select(User).where(User.role.in_(["approver", "requester_approver"]))
    result = await db.execute(stmt)
    approver = result.scalars().first()
    if not approver:
        raise HTTPException(status_code=400, detail="No approver configured")

    req = AccessRequest(
        requester_id=current_user.id,
        approver_id=approver.id,
        breakglass_account_id=account.id,
        reason=reason,
        status="pending",
    )
    db.add(req)
    await db.commit()
    await db.refresh(req)

    send_email(
        to=approver.email,
        subject=f"Breakglass request #{req.id}",
        body=f"Requester: {current_user.username}\nAccount: {account.username}\nReason: {reason}\n"
             f"Approve: https://your-app/ui/approve/{req.id}"
    )

    log_event("REQUEST_CREATED", request_id=req.id, requester=current_user.username)
    return {"id": req.id, "status": req.status}
