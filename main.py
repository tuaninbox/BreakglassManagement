from fastapi import FastAPI
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import Base, engine, AsyncSessionLocal
from core.security import hash_password
#from core.middleware import AuditMiddleware
from models.user import User

from api import auth, devices, accounts, requests, approvals, admin
from ui.routes import auth as ui_auth, accounts as ui_accounts, breakglass as ui_breakglass, devices as ui_devices, approvals as ui_approvals, logs as ui_logs

from core.device_config import load_config
from core.device_loader import load_devices

app = FastAPI(title="Breakglass")
#app.add_middleware(AuditMiddleware)

async def seed_admin_user():
    """
    Create an admin user on first startup if none exists.
    This runs automatically and is idempotent.
    """
    async with AsyncSessionLocal() as db:
        stmt = select(User).where(User.username == "admin")
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            return  # Admin already exists

        admin_user = User(
            username="admin",
            email="admin@example.com",
            role="admin",
            password_hash=hash_password("admin123"),
            is_active=True,
        )

        db.add(admin_user)
        await db.commit()
        print("✔ Admin user created: username=admin password=admin123")


@app.on_event("startup")
async def startup():
    # Load configuration
    app.state.config = load_config()
    print("✔ Loaded configuration:", app.state.config)

    # Optional: preload devices at startup
    try:
        app.state.devices = await load_devices(app.state.config)
        print(f"✔ Loaded {len(app.state.devices)} devices")
    except Exception as e:
        print("⚠ Device load failed:", e)
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed admin user
    await seed_admin_user()


# Routers
app.include_router(auth.router)
app.include_router(devices.router)
app.include_router(accounts.router)
app.include_router(requests.router)
app.include_router(approvals.router)
app.include_router(admin.router)
app.include_router(ui_auth.router)
app.include_router(ui_accounts.router)
app.include_router(ui_breakglass.router)
app.include_router(ui_devices.router)
app.include_router(ui_approvals.router)
app.include_router(ui_logs.router)


# Optional: redirect "/" → "/ui/login"
from fastapi.responses import RedirectResponse

@app.get("/")
async def root():
    return RedirectResponse(url="http://localhost:8000/ui/login")
