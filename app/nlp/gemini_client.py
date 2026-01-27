from app.settings import GEMINI_API_KEY
from google import genai
# import os

client = genai.Client(api_key=GEMINI_API_KEY)

async def gemini_generate(prompt: str) -> str:
    try:
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt
        )

        if hasattr(response, "text") and response.text:
            return response.text.strip()

        try:
            parts = response.candidates[0].content.parts
            if parts and parts[0].text:
                return parts[0].text.strip()
        except Exception:
            pass

        retry_prompt = "Summarize this clearly:\n\n" + prompt[:12000]
        retry = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=retry_prompt
        )

        if hasattr(retry, "text") and retry.text:
            return retry.text.strip()

        return "Unable to generate response (empty model output)."

    except Exception:
        # Never let webhook crash
        raise


async def detect_language_with_gemini(text: str) -> str:
    prompt = f"""
Detect the primary human language of the following text.
Return ONLY the ISO 639-1 two-letter code (like en, hi, ja, zh, fr, de).
No explanation.

Text:
{text}
"""
    result = await gemini_generate(prompt)  
    return result.strip().lower()
