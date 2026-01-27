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

async def github_delete(endpoint: str):
    headers = await _headers()
    async with httpx.AsyncClient() as client:
        r = await client.delete(f"{GITHUB_API}{endpoint}", headers=headers)
        if r.status_code not in (200, 204):
            r.raise_for_status()
        return True

async def get_issue_comments(repo: str, issue_number: int):
    """
    Fetch all comments of an issue / PR (first 100 for now).
    """
    return await github_get(f"/repos/{repo}/issues/{issue_number}/comments?per_page=100")

async def get_user_issues(repo: str, username: str):
    """
    Search issues created by user in this repo.
    """
    return await github_get(f"/search/issues?q=repo:{repo}+type:issue+author:{username}")

async def get_user_prs(repo: str, username: str):
    """
    Search pull requests created by user in this repo.
    """
    return await github_get(f"/search/issues?q=repo:{repo}+type:pr+author:{username}")

async def get_repo_maintainers(repo: str):
    """
    Returns GitHub users with maintain/admin permission.
    """
    owners = await github_get(f"/repos/{repo}/collaborators?permission=maintain")
    admins = await github_get(f"/repos/{repo}/collaborators?permission=admin")

    users = set()
    for u in owners + admins:
        users.add(u["login"])

    return list(users)
