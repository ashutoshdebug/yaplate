from app.nlp.lingo_client import translate
from app.nlp.formatter import format_proxy_reply

async def build_proxy_reply(parent_text, speaker_text, speaker_username, target_lang):
    translated = await translate(speaker_text, target_lang)
    return format_proxy_reply(
        parent_text=parent_text,
        speaker_username=speaker_username,
        translated_text=translated,
        original_text=speaker_text,
        target_lang=target_lang
    )
