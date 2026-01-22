def build_reply_context(payload):
    sender = payload["sender"]["login"]
    return {
        "speaker_username": sender
    }
