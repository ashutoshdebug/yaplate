import re

BOT_MENTION = "@yaplate-bot"


def strip_blockquotes(text: str):
    return "\n".join(
        line for line in text.splitlines()
        if not line.lstrip().startswith(">")
    )


def extract_translation_blocks(lines):
    blocks = []
    i = 0

    while i < len(lines):
        line = lines[i]
        m = re.search(r"Translation\s*\(([a-zA-Z\-]+)\)", line, re.IGNORECASE)

        if m:
            lang = m.group(1).lower()
            j = i + 1

            # skip blank lines
            while j < len(lines) and not lines[j].strip():
                j += 1

            buf = []
            while j < len(lines):
                # stop at next Translation header or command
                if re.search(r"Translation\s*\(", lines[j], re.IGNORECASE):
                    break
                if lines[j].strip().startswith("@"):
                    break
                buf.append(lines[j])
                j += 1

            text = "\n".join(l for l in buf if l.strip()).strip()
            if text:
                blocks.append({
                    "label": f"Translation ({lang})",
                    "lang": lang,
                    "text": text
                })

            i = j
            continue

        i += 1

    return blocks



def extract_thread_summary(lines):
    collecting = False
    buf = []

    for line in lines:
        if re.match(r"#+\s*.*thread summary", line.lower()):
            collecting = True
            buf.append(line)
            continue

        if collecting:
            if re.search(r"translation\s*\(", line.lower()) or line.strip().startswith("@"):
                break
            buf.append(line)

    while buf and not buf[-1].strip():
        buf.pop()

    return "\n".join(buf).strip() if buf else None


def extract_proxy_reply(lines):
    for line in lines:
        if re.search(r"\]\([^)]+\)\s+says\s*:", line):
            return line.strip()
    return None


def parse_translate_command(text: str):
    clean = strip_blockquotes(text)

    if BOT_MENTION not in clean.lower():
        return None

    lang_match = re.search(r"translate.*(?:to|in)\s+([a-zA-Z\-]+)", clean, re.IGNORECASE)
    if not lang_match:
        return None

    target_lang = lang_match.group(1).lower()

    blockquote_lines = []
    for line in text.splitlines():
        if line.lstrip().startswith(">"):
            blockquote_lines.append(re.sub(r"^\s*>+\s?", "", line))

    if not blockquote_lines:
        # Fallback: "double quoted"
        quote_match = re.search(r'"([^"]+)"', text, re.DOTALL)
        if quote_match:
            return {
                "command": "translate",
                "target_lang": target_lang,
                "quoted_text": quote_match.group(1).strip(),
                "quoted_label": None
            }
        return None

    # 1️⃣ ORIGINAL Thread Summary (always highest priority)
    summary_text = extract_thread_summary(blockquote_lines)
    if summary_text:
        return {
            "command": "translate",
            "target_lang": target_lang,
            "quoted_text": summary_text,
            "quoted_label": "Thread Summary"
        }

    # 2️⃣ Proxy reply
    proxy_line = extract_proxy_reply(blockquote_lines)
    if proxy_line:
        return {
            "command": "translate",
            "target_lang": target_lang,
            "quoted_text": proxy_line,
            "quoted_label": "Proxy Reply"
        }

    # 3️⃣ Translation chain (re-translate last non-target language)
    blocks = [b for b in extract_translation_blocks(blockquote_lines) if b["text"]]
    if blocks:
        for b in reversed(blocks):
            if b["lang"] != target_lang:
                return {
                    "command": "translate",
                    "target_lang": target_lang,
                    "quoted_text": b["text"],
                    "quoted_label": b["label"]
                }

        # All blocks already in same language → use last
        b = blocks[-1]
        return {
            "command": "translate",
            "target_lang": target_lang,
            "quoted_text": b["text"],
            "quoted_label": b["label"]
        }

    # 4️⃣ Raw quoted fallback
    return {
        "command": "translate",
        "target_lang": target_lang,
        "quoted_text": "\n".join(blockquote_lines).strip(),
        "quoted_label": None
    }



def parse_reply_command(text: str):
    clean = strip_blockquotes(text)

    if BOT_MENTION not in clean.lower():
        return None

    lang_match = re.search(r"reply.*(?:to|in)\s+([a-zA-Z\-]+)", clean, re.IGNORECASE)
    if not lang_match:
        return None

    target_lang = lang_match.group(1).lower()

    quoted_lines = []
    for line in text.splitlines():
        if line.lstrip().startswith(">"):
            quoted_lines.append(re.sub(r"^\s*>+\s?", "", line))

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
    clean = strip_blockquotes(text)

    if BOT_MENTION not in clean.lower():
        return None

    if "summarize" not in clean.lower():
        return None

    lang_match = re.search(r"summarize.*in\s+([a-zA-Z\-]+)", clean, re.IGNORECASE)
    target_lang = lang_match.group(1).lower() if lang_match else "en"

    return {
        "command": "summarize",
        "target_lang": target_lang
    }
