from fastapi import HTTPException
from typing import Any, Dict

from app.security.webhook_verify import verify_signature
from app.logger import get_logger


logger = get_logger("yaplate.webhooks")


async def handle_github_event(
    event_type: str,
    signature: str,
    payload: Dict[str, Any],
    raw_body: bytes,
):
    """
    Handle and verify incoming GitHub webhook events.
    """
    if not verify_signature(raw_body, signature):
        logger.warning("Invalid GitHub webhook signature")
        raise HTTPException(status_code=401, detail="Invalid GitHub signature")

    logger.info("Verified GitHub event: %s", event_type)

    if event_type == "issue_comment" and isinstance(payload, dict):
        comment = payload.get("comment") or {}
        body = comment.get("body", "")
        author = comment.get("user", {}).get("login")

        logger.info("%s: %s", author, body)

    return {"status": "secure"}
