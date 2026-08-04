from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.db import get_db
from deps.auth import get_current_user
from core.logging import log_event
from models.user import User
from models.account import BreakglassAccount
from models.device import Device
from schemas.account import AccountRead, AccountCreate

router = APIRouter(prefix="/api/accounts", tags=["accounts"])

@router.post("/", response_model=AccountRead, status_code=201)
async def create_account(
    data: AccountCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can create accounts")

    device = await db.get(Device, data.device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    acc = BreakglassAccount(
        device_id=data.device_id,
        username=data.username,
        vault_path=data.vault_path,
        vault_key=data.vault_key,
    )
    db.add(acc)
    await db.commit()
    await db.refresh(acc)
    log_event("ACCOUNT_CREATED", account_id=acc.id, device_id=acc.device_id)
    return acc

@router.get("/", response_model=list[AccountRead])
async def list_accounts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = select(BreakglassAccount)
    result = await db.execute(stmt)
    accounts = result.scalars().all()
    return accounts
