import logging

logger = logging.getLogger("yaplate.llm")

FALLBACK_MESSAGE = "LLM service is temporarily unavailable. Please try again later."

async def safe_llm_call(fn, *args, **kwargs):
    try:
        return await fn(*args, **kwargs)
    except Exception as e:
        logger.exception("LLM call failed", exc_info=e)
        return FALLBACK_MESSAGE
