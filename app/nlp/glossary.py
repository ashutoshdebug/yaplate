def build_reference(target_lang: str):
    """
    Returns reference data for Lingo.dev.

    Structure:
    {
      "ja": {"GitHub": "GitHub", "Pull Request": "プルリクエスト"},
      "hi": {"GitHub": "GitHub", "Pull Request": "पुल रिक्वेस्ट"}
    }
    """
    if not target_lang:
        return {}

    target_lang = target_lang.strip().lower()

    BASE = {
        "GitHub": {
            "ja": "GitHub",
            "hi": "GitHub",
        },
        "Pull Request": {
            "ja": "プルリクエスト",
            "hi": "पुल रिक्वेस्ट",
        },
        "FastAPI": {
            "ja": "FastAPI",
            "hi": "FastAPI",
        },
    }

    reference = {}

    for term, langs in BASE.items():
        if target_lang in langs:
            reference.setdefault(target_lang, {})[term] = langs[target_lang]

    return reference
