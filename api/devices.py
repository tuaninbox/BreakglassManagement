from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.db import get_db
from deps.auth import get_current_user
from core.logging import log_event
from core.nagios import get_hostgroups, get_devices_from_hostgroup
from models.user import User
from models.device import Device
from schemas.device import DeviceRead, DeviceCreate, DeviceImportItem

router = APIRouter(prefix="/api/devices", tags=["devices"])

@router.get("/", response_model=list[DeviceRead])
async def list_devices(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = select(Device)
    result = await db.execute(stmt)
    devices = result.scalars().all()
    return devices

@router.post("/", response_model=DeviceRead, status_code=201)
async def create_device(
    data: DeviceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can create devices")

    device = Device(name=data.name, description=data.description)
    db.add(device)
    await db.commit()
    await db.refresh(device)
    log_event("DEVICE_CREATED", device_id=device.id, name=device.name)
    return device

@router.get("/nagios/hostgroups")
async def list_nagios_hostgroups(
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can query Nagios")
    hostgroups = await get_hostgroups()
    return hostgroups

@router.post("/nagios/sync", response_model=list[DeviceRead])
async def sync_devices_from_nagios(
    hostgroup_name: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can sync devices")

    devices_data = await get_devices_from_hostgroup(hostgroup_name)
    created_devices = []

    for d in devices_data:
        stmt = select(Device).where(Device.name == d["name"])
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()
        if existing:
            continue
        device = Device(name=d["name"], description=d.get("description"))
        db.add(device)
        created_devices.append(device)

    await db.commit()
    for device in created_devices:
        await db.refresh(device)
        log_event("DEVICE_SYNCED_FROM_NAGIOS", device_id=device.id, name=device.name, hostgroup=hostgroup_name)

    return created_devices

@router.post("/import-local", response_model=list[DeviceRead])
async def import_local_devices(
    items: list[DeviceImportItem],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can import devices")

    created_devices = []
    for item in items:
        stmt = select(Device).where(Device.name == item.name)
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()
        if existing:
            continue
        device = Device(name=item.name, description=item.description)
        db.add(device)
        created_devices.append(device)

    await db.commit()
    for device in created_devices:
        await db.refresh(device)
        log_event("DEVICE_IMPORTED_LOCAL", device_id=device.id, name=device.name)

    return created_devices
