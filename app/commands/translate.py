import re
from app.nlp.lingo_client import translate
from app.nlp.formatter import format_quoted_translation


def clean_markdown(text: str) -> str:
    # Remove bold/italic markers
    text = re.sub(r"\*{1,3}", "", text)
    # Remove leftover block labels
    text = re.sub(r"Translation\s*\([a-zA-Z\-]+\)\s*:", "", text)
    return text.strip()


async def translate_and_format(original_text, target_lang, quoted_label=None, user_message=None):
    clean_text = clean_markdown(original_text)
    translated = await translate(clean_text, target_lang)
    return format_quoted_translation(clean_text, target_lang, translated, quoted_label)
