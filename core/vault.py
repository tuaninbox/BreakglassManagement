import httpx
from core.settings import settings

async def get_secret(path: str) -> dict:
    url = f"{settings.vault_addr}/v1/{path}"
    headers = {"X-Vault-Token": settings.vault_token}
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=headers)
        resp.raise_for_status()
        return resp.json()["data"]
