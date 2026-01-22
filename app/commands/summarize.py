from app.github.api import get_issue_comments
from app.nlp.context_builder import build_thread_context, chunk_thread_context
from app.nlp.formatter import format_thread_summary
from app.nlp.lingo_client import translate
from app.nlp.gemini_client import gemini_generate


async def summarize_chunk(chunk):
    prompt = "Summarize the following discussion clearly:\n\n"
    for msg in chunk:
        prompt += f"{msg['user']}: {msg['text']}\n\n"

    return await gemini_generate(prompt)


async def merge_summaries(summaries):
    prompt = """
Merge the following summaries into a structured executive summary with sections:
Context, Key Points, Decisions, Problems, Solutions, Open Questions.

Summaries:
"""
    for s in summaries:
        prompt += s + "\n\n"

    return await gemini_generate(prompt)


async def summarize_thread(repo: str, issue_number: int, target_lang: str):
    comments = await get_issue_comments(repo, issue_number)
    context = build_thread_context(comments)

    if not context:
        return "No discussion found to summarize."

    chunks = chunk_thread_context(context, chunk_size=15)

    chunk_summaries = []
    for chunk in chunks:
        s = await summarize_chunk(chunk)
        chunk_summaries.append(s)

    final_summary_en = await merge_summaries(chunk_summaries)

    if target_lang != "en":
        final_summary = await translate(final_summary_en, target_lang)
    else:
        final_summary = final_summary_en

    return format_thread_summary(final_summary, target_lang)
