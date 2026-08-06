from urllib import response

from fastapi import APIRouter, Request, Depends, Form, Response
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.db import get_db
from deps.auth import get_current_user_optional
from core.security import verify_password, create_access_token, hash_password
from models.user import User
from core.device_loader import load_devices
from core.audit_logger import log_action

router = APIRouter(prefix="/ui", tags=["ui"])
templates = Jinja2Templates(directory="ui/templates")
templates.env.cache.clear()


@router.get("/devices", response_class=HTMLResponse)
async def devices_page(
    request: Request,
    search: str = "",
    filter_os: str = "",
    filter_location: str = "",
    sort: str = "",
    current_user: User | None = Depends(get_current_user_optional),
):
    # If user is not logged in → redirect to login
    if current_user is None:
        return RedirectResponse("/ui/login")
    
    cfg = request.app.state.config
    devices = await load_devices(cfg)

    # Filtering
    if search:
        s = search.lower()
        devices = [
            d for d in devices
            if s in d["name"].lower()
            or s in d["ip"].lower()
            or s in d["os"].lower()
            or s in d["location"].lower()
        ]

    if filter_os:
        devices = [d for d in devices if d["os"] == filter_os]

    if filter_location:
        devices = [d for d in devices if d["location"] == filter_location]

    # Sorting
    if sort in ("name", "ip", "location", "os"):
        devices = sorted(devices, key=lambda x: x[sort])

    # HTMX request → return only table fragment
    if request.headers.get("HX-Request") == "true":
        return templates.TemplateResponse(
            "partials/device_table.html",
            {"request": request, "devices": devices},
        )

    # Normal full-page load
    return templates.TemplateResponse(
        "devices.html",
        {"request": request, "current_user": current_user, "devices": devices},
    )

