import re

BOT_MENTION = "@yaplate-bot"

def parse_translate_command(text: str):
    if BOT_MENTION not in text.lower():
        return None

    # Extract target language
    lang_match = re.search(r"translate.*to\s+([a-zA-Z\-]+)", text, re.IGNORECASE)
    if not lang_match:
        return None
    target_lang = lang_match.group(1).lower()

    # 1. Try extracting from "double quotes"
    quote_match = re.search(r'"([^"]+)"', text, re.DOTALL)
    if quote_match:
        quoted_text = quote_match.group(1).strip()
    else:
        # 2. Fallback: extract from GitHub blockquote (> ...)
        blockquote_lines = []
        for line in text.splitlines():
            if line.strip().startswith(">"):
                blockquote_lines.append(line.lstrip("> ").strip())

        if not blockquote_lines:
            return None

        quoted_text = "\n".join(blockquote_lines)

    return {
        "target_lang": target_lang,
        "quoted_text": quoted_text
    }
