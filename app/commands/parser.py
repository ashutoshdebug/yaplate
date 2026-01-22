import re

BOT_MENTION = "@yaplate-bot"

def extract_translation_block(lines):
    for i, line in enumerate(lines):
        m = re.search(r"(Translation\s*\([a-zA-Z\-]+\))\s*:\s*(.+)", line)
        if m:
            clean_text = re.sub(r"^\*+|\*+$", "", m.group(2)).strip()
            return {"label": m.group(1), "text": clean_text}

        m2 = re.search(r"(Translation\s*\([a-zA-Z\-]+\))\s*:", line)
        if m2 and i + 1 < len(lines):
            clean_text = re.sub(r"^\*+|\*+$", "", lines[i + 1]).strip()
            return {"label": m2.group(1), "text": clean_text}

    return None



def parse_translate_command(text: str):
    if BOT_MENTION not in text.lower():
        return None

    lang_match = re.search(r"translate.*(?:to|in)\s+([a-zA-Z\-]+)", text, re.IGNORECASE)
    if not lang_match:
        return None
    target_lang = lang_match.group(1).lower()

    # 1. Extract GitHub blockquotes (supports nested > > >)
    blockquote_lines = []
    for line in text.splitlines():
        if line.lstrip().startswith(">"):
            clean = re.sub(r"^\s*>+\s?", "", line)
            blockquote_lines.append(clean)

    if blockquote_lines:
        # A. Prefer translating a bot Translation(...) block
        translation_block = extract_translation_block(blockquote_lines)
        if translation_block:
            return {
                "target_lang": target_lang,
                "quoted_text": translation_block["text"],
                "quoted_label": translation_block["label"]
            }

        # B. Otherwise translate full quoted content
        return {
            "target_lang": target_lang,
            "quoted_text": "\n".join(blockquote_lines).strip(),
            "quoted_label": None
        }

    # 2. Fallback: extract from "double quotes" only if no blockquote exists
    quote_match = re.search(r'"([^"]+)"', text, re.DOTALL)
    if quote_match:
        return {
            "target_lang": target_lang,
            "quoted_text": quote_match.group(1).strip(),
            "quoted_label": None
        }

    return None

def parse_reply_command(text: str):
    if BOT_MENTION not in text.lower():
        return None

    lang_match = re.search(r"reply.*(?:to|in)\s+([a-zA-Z\-]+)", text, re.IGNORECASE)
    if not lang_match:
        return None

    target_lang = lang_match.group(1).lower()

    # Extract quoted parent (first person)
    quoted_lines = []
    for line in text.splitlines():
        if line.lstrip().startswith(">"):
            clean = re.sub(r"^\s*>+\s?", "", line)
            quoted_lines.append(clean)

    if not quoted_lines:
        return None

    # Extract second person's message (non-quoted, non-command)
    body_lines = []
    for line in text.splitlines():
        if not line.strip().startswith(">") and BOT_MENTION not in line:
            if line.strip():
                body_lines.append(line.strip())

    if not body_lines:
        return None

    return {
        "command": "reply",
        "target_lang": target_lang,
        "parent_text": "\n".join(quoted_lines).strip(),
        "speaker_text": "\n".join(body_lines).strip()
    }
