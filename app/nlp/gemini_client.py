from google import genai
import os

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

async def gemini_generate(prompt: str) -> str:
    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=prompt
    )

    # 1) Normal fast path
    if hasattr(response, "text") and response.text:
        return response.text.strip()

    # 2) Candidate structured path
    try:
        parts = response.candidates[0].content.parts
        if parts and parts[0].text:
            return parts[0].text.strip()
    except Exception:
        pass

    # 3) Fallback: re-ask in minimal form
    retry_prompt = (
        "Summarize this clearly and concisely:\n\n"
        + prompt[:12000]  # safety truncation
    )

    retry = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=retry_prompt
    )

    if hasattr(retry, "text") and retry.text:
        return retry.text.strip()

    # 4) Absolute last resort (never crash webhook)
    return "⚠️ Unable to generate summary (model returned empty content). Please try again."
