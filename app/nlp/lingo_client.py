from lingodotdev.engine import LingoDotDevEngine
import os

API_KEY = os.getenv("LINGO_API_KEY")

async def translate(text: str, target: str) -> str:
    return await LingoDotDevEngine.quick_translate(
        text,
        api_key=API_KEY,
        target_locale=target
    )
