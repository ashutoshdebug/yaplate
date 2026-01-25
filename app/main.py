from app import settings  # load .env
from fastapi import FastAPI, Request, Header, HTTPException
from app.security.webhook_verify import verify_signature
from app.github.events import handle_event
from app.logger import get_logger

app = FastAPI()
logger = get_logger()

@app.post("/webhook")
async def github_webhook(
    request: Request,
    x_hub_signature_256: str = Header(None),
    x_github_event: str = Header(None),
):
    body = await request.body()

    if not verify_signature(body, x_hub_signature_256):
        raise HTTPException(status_code=401, detail="Invalid signature")

    payload = await request.json()
    logger.info(f"Received event: {x_github_event}")

    await handle_event(x_github_event, payload)
    return {"status": "ok"}


# 👇 This makes `python -m app.main` work like before
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)
