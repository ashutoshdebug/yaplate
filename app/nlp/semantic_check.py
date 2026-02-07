from app.logger import get_logger

logger = get_logger("yaplate.nlp.semantic_check")

# Keep these strict. Avoid generic words like "issue", "update", "progress".
KEYWORDS = [
    "maintainer",
    "needs maintainer",
    "waiting for maintainer",
    "waiting for review",
    "waiting for reviewer",
    "reviewer",
    "review",
    "merge",
    "merging",
    "approval",
    "approve",
    "blocked",
    "stuck",
]

BOT_MENTIONS = ["@yaplate-bot", "yaplate-bot", "yaplate", "@yaplate"]


async def wants_maintainer_attention(text: str) -> bool:
    """
    Deterministic check only.

    This is used to STOP followups, so false positives are expensive.
    """
    text = text or ""
    text_l = text.lower()

    # Ignore if user is talking to the bot
    if any(b in text_l for b in BOT_MENTIONS):
        return False

    return any(k in text_l for k in KEYWORDS)
