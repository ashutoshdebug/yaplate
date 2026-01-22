from fastapi import HTTPException
from app.security.webhook_verify import verify_signature
import logging

logger = logging.getLogger("yaplate.webhooks")


async def handle_github_event(event_type: str, signature: str, payload: dict, raw_body: bytes):
    if not verify_signature(raw_body, signature):
        raise HTTPException(status_code=401, detail="Invalid GitHub signature")

    logger.info(f"Verified GitHub event: {event_type}")

    if event_type == "issue_comment":
        comment = payload.get("comment", {})
        body = comment.get("body", "")
        author = comment.get("user", {}).get("login")
        logger.info(f"{author}: {body}")

    return {"status": "secure"}
