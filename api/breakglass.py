from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from models.breakglass_request import BreakglassRequest
from models.user import User
from deps.auth import get_current_user
from deps.db import get_db
from core.audit_logger import log_action

router = APIRouter(prefix="/api/breakglass", tags=["breakglass"])

@router.post("/create")
async def create_breakglass_request(
    request: Request,
    payload: BreakglassRequestCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Create request
    req = BreakglassRequest(
        requester_id=current_user.id,
        device_id=payload.device_id,
        reason=payload.reason,
        status="pending",
    )

    db.add(req)
    await db.commit()
    await db.refresh(req)

    log_action(
        current_user,
        "breakglass_request_create",
        f"Created breakglass request {req.id} for device {payload.device_id}",
        request,
        category="breakglass",
    )

    return {"success": True, "request_id": req.id}
