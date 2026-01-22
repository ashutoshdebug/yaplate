import jwt
import time
import httpx
from app.settings import GITHUB_APP_ID, GITHUB_PRIVATE_KEY_PATH

with open(GITHUB_PRIVATE_KEY_PATH, "r") as f:
    PRIVATE_KEY = f.read()

def create_jwt():
    now = int(time.time())
    payload = {
        "iat": now - 30,
        "exp": now + 9 * 60,
        "iss": int(GITHUB_APP_ID)
    }
    return jwt.encode(payload, PRIVATE_KEY, algorithm="RS256")

async def get_installation_token():
    jwt_token = create_jwt()

    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Accept": "application/vnd.github+json"
    }

    async with httpx.AsyncClient() as client:
        installations = await client.get(
            "https://api.github.com/app/installations",
            headers=headers
        )

        print("GitHub App authenticated successfully")


        installations.raise_for_status()

        installation_id = installations.json()[0]["id"]

        token_resp = await client.post(
            f"https://api.github.com/app/installations/{installation_id}/access_tokens",
            headers=headers
        )
        token_resp.raise_for_status()

        return token_resp.json()["token"]
