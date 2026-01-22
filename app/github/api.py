import os
import httpx
from app.github.auth import get_installation_token

GITHUB_API = "https://api.github.com"

async def github_post(endpoint: str, json: dict):
    token = await get_installation_token()

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{GITHUB_API}{endpoint}",
            headers=headers,
            json=json
        )
        response.raise_for_status()
        return response.json()
