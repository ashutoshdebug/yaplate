from app.nlp.lingo_client import translate
from app.nlp.formatter import format_quoted_translation

async def translate_and_format(original_text, target_lang, quoted_label=None, user_message=None):
    translated = await translate(original_text, target_lang)
    return format_quoted_translation(original_text, target_lang, translated, quoted_label)
