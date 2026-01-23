from google import genai
import os

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

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

        return "⚠️ Unable to generate response (empty model output)."

    except Exception:
        # Never let webhook crash
        raise
