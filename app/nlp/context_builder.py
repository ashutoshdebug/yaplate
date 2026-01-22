def build_reply_context(payload):
    sender = payload["sender"]["login"]
    return {
        "speaker_username": sender
    }


def build_thread_context(comments):
    """
    Build clean thread context for summarization.
    Removes bot messages and keeps username attribution.
    """
    cleaned = []
    for c in comments:
        user = c["user"]["login"]
        body = c["body"]

        # Skip bot messages
        if user.lower().endswith("[bot]") or user.lower() == "yaplate-bot":
            continue

        cleaned.append({
            "user": user,
            "text": body
        })

    return cleaned


def chunk_thread_context(context, chunk_size=15):
    """
    Split thread into chunks of N messages for hierarchical summarization.
    """
    chunks = []
    for i in range(0, len(context), chunk_size):
        chunks.append(context[i:i + chunk_size])
    return chunks
