import re

from app.nlp.lingo_client import translate
from app.nlp.formatter import format_quoted_translation
from app.nlp.llm_guard import FALLBACK_MESSAGE


def clean_markdown(text: str) -> str:
    text = text or ""
    text = re.sub(r"\*{1,3}", "", text)
    text = re.sub(r"Translation\s*\([a-zA-Z\-]+\)\s*:", "", text)
    return text.strip()


async def translate_and_format(
    original_text,
    target_lang,
    quoted_label=None,
    user_message=None,
):
    """
    Translate quoted text and format output.
    Formatting and fallback behavior are intentionally stable.
    """
    clean_text = clean_markdown(original_text)

    try:
        translated = await translate(clean_text, target_lang)
    except Exception:
        translated = FALLBACK_MESSAGE

    translated = translated or ""

    # If LLM failed → no Translation(xx) header
    if translated.strip() == FALLBACK_MESSAGE:
        quoted = "\n".join(
            f"> {line}" for line in clean_text.splitlines()
        )
        return f"""{quoted}

 {FALLBACK_MESSAGE}"""

    # Normal success path
    return format_quoted_translation(
        clean_text,
        target_lang,
        translated,
        quoted_label,
    )
