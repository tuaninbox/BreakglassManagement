from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from deps.auth import get_current_user_optional
from core.db import get_db
from models.breakglass_request import BreakglassRequest
from models.user import User
from core.audit_logger import log_action
from ui import templates

router = APIRouter()

@router.get("/ui/approve/requests")
async def approve_requests_page(
    request: Request,
    current_user: User | None = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    if current_user is None:
        return RedirectResponse("/ui/login")

    if current_user.role not in ["approver", "requester_approver", "admin"]:
        return RedirectResponse("/ui")

    stmt = select(BreakglassRequest).where(BreakglassRequest.status == "pending")
    pending = (await db.execute(stmt)).scalars().all()

    log_action(
        current_user,
        "approver_view_pending",
        f"Viewed {len(pending)} pending requests",
        request,
        category="breakglass",
    )

    return templates.TemplateResponse(
        "approve_requests.html",
        {
            "request": request,
            "current_user": current_user,
            "pending": pending,
        },
    )


@router.post("/ui/approve/requests/{req_id}/approve")
async def approve_request(
    req_id: int,
    request: Request,
    current_user: User | None = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    if current_user is None:
        return RedirectResponse("/ui/login")

    if current_user.role not in ["approver", "requester_approver", "admin"]:
        return RedirectResponse("/ui")

    stmt = select(BreakglassRequest).where(BreakglassRequest.id == req_id)
    req = (await db.execute(stmt)).scalar_one_or_none()

    if not req:
        return RedirectResponse("/ui/approve/requests?error=notfound")

    req.status = "approved"
    req.approver_id = current_user.id
    await db.commit()

    log_action(
        current_user,
        "breakglass_request_approved",
        f"Approved request {req_id}",
        request,
        category="breakglass",
    )

    return RedirectResponse("/ui/approve/requests?success=approved")


@router.post("/ui/approve/requests/{req_id}/reject")
async def reject_request(
    req_id: int,
    request: Request,
    current_user: User | None = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    if current_user is None:
        return RedirectResponse("/ui/login")

    if current_user.role not in ["approver", "requester_approver", "admin"]:
        return RedirectResponse("/ui")

    stmt = select(BreakglassRequest).where(BreakglassRequest.id == req_id)
    req = (await db.execute(stmt)).scalar_one_or_none()

    if not req:
        return RedirectResponse("/ui/approve/requests?error=notfound")

    req.status = "rejected"
    req.approver_id = current_user.id
    await db.commit()

    log_action(
        current_user,
        "breakglass_request_rejected",
        f"Rejected request {req_id}",
        request,
        category="breakglass",
    )

    return RedirectResponse("/ui/approve/requests?success=rejected")
