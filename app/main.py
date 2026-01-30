from app import settings  # load .env
from fastapi import FastAPI, Request, Header, HTTPException
from contextlib import asynccontextmanager
import asyncio

from app.security.webhook_verify import verify_signature
from app.github.events import handle_event
from app.logger import get_logger
from app.workers.followup_scheduler import followup_loop
from app.settings import validate_github_settings


logger = get_logger()

_scheduler_task: asyncio.Task | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _scheduler_task

    # Validate critical configuration early
    validate_github_settings()

    # Startup: start background follow-up scheduler
    _scheduler_task = asyncio.create_task(followup_loop())
    logger.info("Follow-up scheduler started")

    try:
        yield
    finally:
        # Shutdown: cancel background task cleanly
        if _scheduler_task:
            _scheduler_task.cancel()
            try:
                await _scheduler_task
            except asyncio.CancelledError:
                pass
            logger.info("Follow-up scheduler stopped")


app = FastAPI(lifespan=lifespan)


@app.post("/webhook")
async def github_webhook(
    request: Request,
    x_hub_signature_256: str | None = Header(None),
    x_github_event: str | None = Header(None),
):
    body = await request.body()

    if not x_hub_signature_256:
        raise HTTPException(status_code=401, detail="Missing signature header")

    if not verify_signature(body, x_hub_signature_256):
        raise HTTPException(status_code=401, detail="Invalid signature")

    if not x_github_event:
        raise HTTPException(status_code=400, detail="Missing GitHub event header")

    payload = await request.json()
    logger.info("Received GitHub event: %s", x_github_event)

    await handle_event(x_github_event, payload)
    return {"status": "ok"}


# 👇 This makes `python -m app.main` work like before
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
    )
