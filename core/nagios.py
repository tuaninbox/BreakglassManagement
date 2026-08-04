import httpx
from typing import List, Dict
from core.config import settings

# These endpoints are examples; adjust to your Nagios XI/Core API.
# Idea: get hostgroups, then hosts in a hostgroup.

async def get_hostgroups() -> List[Dict]:
    """
    Return list of hostgroups from Nagios.
    """
    if not settings.nagios_api_token:
        return []

    url = f"{settings.nagios_url}/nagiosxi/api/v1/config/hostgroup"
    params = {"apikey": settings.nagios_api_token}
    async with httpx.AsyncClient(verify=settings.nagios_verify_ssl) as client:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()
        # Normalize to [{'name': ..., 'alias': ...}, ...]
        return [
            {"name": hg.get("hostgroup_name"), "alias": hg.get("alias")}
            for hg in data.get("hostgroups", [])
        ]

async def get_devices_from_hostgroup(hostgroup_name: str) -> List[Dict]:
    """
    Return list of devices (hosts) in a given hostgroup.
    """
    if not settings.nagios_api_token:
        return []

    url = f"{settings.nagios_url}/nagiosxi/api/v1/objects/host"
    params = {
        "apikey": settings.nagios_api_token,
        "hostgroup_name": hostgroup_name,
    }
    async with httpx.AsyncClient(verify=settings.nagios_verify_ssl) as client:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()
        devices = []
        for host in data.get("host", []):
            devices.append(
                {
                    "name": host.get("host_name"),
                    "description": host.get("display_name") or host.get("host_name"),
                }
            )
        return devices
