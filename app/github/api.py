import httpx
from app.github.auth import get_installation_token

GITHUB_API = "https://api.github.com"

async def _headers():
    token = await get_installation_token()
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }

async def github_post(endpoint: str, json: dict):
    headers = await _headers()
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{GITHUB_API}{endpoint}", headers=headers, json=json)
        r.raise_for_status()
        return r.json()

async def github_patch(endpoint: str, json: dict):
    headers = await _headers()
    async with httpx.AsyncClient() as client:
        r = await client.patch(f"{GITHUB_API}{endpoint}", headers=headers, json=json)
        r.raise_for_status()
        return r.json()
