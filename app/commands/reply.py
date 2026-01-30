from app.nlp.lingo_client import translate
from app.nlp.formatter import format_proxy_reply


async def build_proxy_reply(
    parent_text,
    speaker_text,
    speaker_username,
    target_lang,
):
    """
    Build a proxy reply by translating speaker text and formatting output.
    Behavior and formatting are intentionally stable.
    """
    parent_text = parent_text or ""
    speaker_text = speaker_text or ""
    speaker_username = speaker_username or ""

    translated = await translate(speaker_text, target_lang)

    return format_proxy_reply(
        parent_text=parent_text,
        speaker_username=speaker_username,
        translated_text=translated,
        original_text=speaker_text,
        target_lang=target_lang,
    )
