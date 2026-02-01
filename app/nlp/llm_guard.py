from app.logger import get_logger
from app.settings import FALLBACK_MESSAGE_TEMPLATE


logger = get_logger("yaplate.llm")

FALLBACK_MESSAGE = FALLBACK_MESSAGE_TEMPLATE


async def safe_llm_call(fn, *args, **kwargs):
    """
    Safely execute an async LLM call.

    On any exception:
    - logs the error
    - returns FALLBACK_MESSAGE
    """
    try:
        return await fn(*args, **kwargs)
    except Exception:
        logger.exception("LLM call failed")
        return FALLBACK_MESSAGE
