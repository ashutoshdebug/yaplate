def build_reference(target_lang: str):
    """
    Returns reference data for Lingo.dev.
    Structure:
    {
      "ja": {"GitHub": "ギットハブ", "Pull Request": "プルリクエスト"},
      "hi": {"GitHub": "गिटहब"}
    }
    """

    BASE = {
        "GitHub": {
            "ja": "GitHub",
            "hi": "GitHub"
        },
        "Pull Request": {
            "ja": "プルリクエスト",
            "hi": "पुल रिक्वेस्ट"
        },
        "FastAPI": {
            "ja": "FastAPI",
            "hi": "FastAPI"
        }
    }

    reference = {}
    for term, langs in BASE.items():
        if target_lang in langs:
            reference.setdefault(target_lang, {})[term] = langs[target_lang]

    return reference
