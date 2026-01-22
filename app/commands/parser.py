import re

BOT_MENTION = "@yaplate-bot"


def extract_translation_blocks(lines):
    """
    Extract all Translation(xx) blocks from quoted text.
    Returns:
    [
      { "label": "Translation (hi)", "lang": "hi", "text": "हे" },
      { "label": "Translation (en)", "lang": "en", "text": "Hey" }
    ]
    """
    blocks = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Inline: **Translation (hi):** हे
        m = re.search(
            r"\*{0,2}Translation\s*\(([a-zA-Z\-]+)\)\*{0,2}\s*:\s*(.+)",
            line
        )

        if m:
            blocks.append({
                "label": f"Translation ({m.group(1)})",
                "lang": m.group(1).lower(),
                "text": m.group(2).strip()
            })
            i += 1
            continue

        # Multiline:
        # **Translation (hi):**
        # हे
        m2 = re.search(
            r"\*{0,2}Translation\s*\(([a-zA-Z\-]+)\)\*{0,2}\s*:",
            line
        )
        if m2 and i + 1 < len(lines):
            blocks.append({
                "label": f"Translation ({m2.group(1)})",
                "lang": m2.group(1).lower(),
                "text": lines[i + 1].strip()
            })
            i += 2
            continue

        i += 1

    return blocks



def parse_translate_command(text: str):
    if BOT_MENTION not in text.lower():
        return None

    lang_match = re.search(r"translate.*(?:to|in)\s+([a-zA-Z\-]+)", text, re.IGNORECASE)
    if not lang_match:
        return None

    target_lang = lang_match.group(1).lower()

    # Extract quoted content
    blockquote_lines = []
    for line in text.splitlines():
        if line.lstrip().startswith(">"):
            clean = re.sub(r"^\s*>+\s?", "", line)
            blockquote_lines.append(clean)

    if blockquote_lines:
        blocks = extract_translation_blocks(blockquote_lines)

        # Prefer block in different language (for re-translation)
        if blocks:
            for b in reversed(blocks):
                if b["lang"] != target_lang:
                    return {
                        "command": "translate",
                        "target_lang": target_lang,
                        "quoted_text": b["text"],
                        "quoted_label": b["label"]
                    }

            # Fallback: last block
            b = blocks[-1]
            return {
                "command": "translate",
                "target_lang": target_lang,
                "quoted_text": b["text"],
                "quoted_label": b["label"]
            }

        # No Translation() blocks → translate full quoted text
        return {
            "command": "translate",
            "target_lang": target_lang,
            "quoted_text": "\n".join(blockquote_lines).strip(),
            "quoted_label": None
        }

    # Fallback: double quotes
    quote_match = re.search(r'"([^"]+)"', text, re.DOTALL)
    if quote_match:
        return {
            "command": "translate",
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

    quoted_lines = []
    for line in text.splitlines():
        if line.lstrip().startswith(">"):
            clean = re.sub(r"^\s*>+\s?", "", line)
            quoted_lines.append(clean)

    if not quoted_lines:
        return None

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


def parse_summarize_command(text: str):
    if BOT_MENTION not in text.lower():
        return None

    if "summarize" not in text.lower():
        return None

    lang_match = re.search(r"summarize.*in\s+([a-zA-Z\-]+)", text, re.IGNORECASE)
    target_lang = lang_match.group(1).lower() if lang_match else "en"

    return {
        "command": "summarize",
        "target_lang": target_lang
    }
