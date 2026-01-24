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

async def github_get(endpoint: str):
    headers = await _headers()
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{GITHUB_API}{endpoint}", headers=headers)
        r.raise_for_status()
        return r.json()

async def get_issue_comments(repo: str, issue_number: int):
    """
    Fetch all comments of an issue / PR (first 100 for now).
    Later we can add pagination if needed.
    """
    return await github_get(f"/repos/{repo}/issues/{issue_number}/comments?per_page=100")

async def github_delete(endpoint: str):
    headers = await _headers()
    async with httpx.AsyncClient() as client:
        r = await client.delete(f"{GITHUB_API}{endpoint}", headers=headers)
        # GitHub returns 204 No Content on success
        if r.status_code not in (200, 204):
            r.raise_for_status()
        return True

async def get_user_issues(repo: str, username: str):
    return await github_get(f"/search/issues?q=repo:{repo}+type:issue+author:{username}")
