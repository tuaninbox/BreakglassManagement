from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse
from models.user import User
from deps.auth import get_current_user_optional
from core.audit_logger import log_action
from core.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

@router.get("/requests/create")
async def breakglass_request_page(
    request: Request,
    current_user: User | None = Depends(get_current_user_optional),
):
    if current_user is None:
        return RedirectResponse("/ui/login")

    return templates.TemplateResponse(
        "breakglass_request_create.html",
        {"request": request, "current_user": current_user},
    )


@router.post("/requests/create")
async def breakglass_request_submit(
    request: Request,
    device_id: int = Form(...),
    reason: str = Form(...),
    current_user: User | None = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    if current_user is None:
        return RedirectResponse("/ui/login")

    req = BreakglassRequest(
        requester_id=current_user.id,
        device_id=device_id,
        reason=reason,
        status="pending",
    )

    db.add(req)
    await db.commit()

    log_action(
        current_user,
        "breakglass_request_create",
        f"Created breakglass request {req.id}",
        request,
        category="breakglass",
    )

    return RedirectResponse("/ui/requests?success=1", status_code=302)
