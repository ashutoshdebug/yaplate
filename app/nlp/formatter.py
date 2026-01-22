def format_quoted_translation(original_text, target_lang, translated_text):
    return f"""> "{original_text}"

**Translation ({target_lang}):**
{translated_text}
"""
