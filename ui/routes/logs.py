from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse

from deps.auth import get_current_user_optional
from models.user import User
from core.audit_logger import log_action
from core.audit_logger import LOG_PATH
import json

router = APIRouter(prefix="/ui", tags=["ui"])
templates = Jinja2Templates(directory="ui/templates")
templates.env.cache.clear()

@router.get("/logs", response_class=HTMLResponse)
async def view_logs(
    request: Request,
    current_user: User | None = Depends(get_current_user_optional),
    user: str | None = None,
    category: str | None = None,
    search: str | None = None,
    limit: int = 300,
):
    logs = []

    if current_user is None or current_user.role != "admin":
        log_action(
            current_user,
            "logs_view",
            "Redirected to login page due to unauthenticated access attempt",
            request,
            category="logs"
        )
        return RedirectResponse("/ui/login")
    
    # Read from the actual audit log file
    try:
        with open(LOG_PATH, "r") as f:
            for line in f:
                try:
                    entry = json.loads(line)
                except:
                    continue

                # Apply filters
                if user and entry.get("user") != user:
                    continue

                if category and entry.get("category") != category:
                    continue

                if search:
                    text = json.dumps(entry).lower()
                    if search.lower() not in text:
                        continue

                logs.append(entry)

    except FileNotFoundError:
        logs = []

    # Show newest logs first
    logs = logs[-limit:]
    logs.reverse()

    log_action(
            current_user,
            "logs_view",
            "Viewed audit logs",
            request,
            category="logs"
        )
    return templates.TemplateResponse(
        "logs.html",
        {
            "request": request,
            "logs": logs,
            "filter_user": user,
            "filter_category": category,
            "filter_search": search,
            "current_user": current_user,
        },
    )
