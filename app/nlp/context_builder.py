from typing import Any, Dict, List

from app.logger import get_logger


logger = get_logger("yaplate.nlp.context_builder")

BOT_NAME = "yaplate"


def build_reply_context(payload: Dict[str, Any]) -> Dict[str, str]:
    """
    Build minimal context for proxy replies.
    """
    try:
        sender = payload.get("sender", {}).get("login")
        if sender:
            return {"speaker_username": sender}
    except Exception:
        logger.exception("Failed to build reply context")

    # Fallback: preserve contract
    return {"speaker_username": ""}


def build_thread_context(comments: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """
    Build clean thread context for summarization.
    Removes bot messages and keeps username attribution.
    """
    cleaned: List[Dict[str, str]] = []

    for c in comments:
        try:
            user = c.get("user", {}).get("login")
            body = c.get("body")

            if not user or body is None:
                continue

            # Skip bot messages
            user_l = user.lower()
            if user_l.endswith("[bot]") or user_l == BOT_NAME:
                continue

            cleaned.append({
                "user": user,
                "text": body,
            })
        except Exception:
            logger.exception("Failed to process comment for thread context")

    return cleaned


def chunk_thread_context(
    context: List[Dict[str, str]],
    chunk_size: int = 15,
) -> List[List[Dict[str, str]]]:
    """
    Split thread into chunks of N messages for hierarchical summarization.
    """
    if chunk_size <= 0:
        return []

    chunks: List[List[Dict[str, str]]] = []
    for i in range(0, len(context), chunk_size):
        chunks.append(context[i:i + chunk_size])

    return chunks
