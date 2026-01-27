import asyncio
import time

from app.cache.store import (
    get_due_followups,
    get_followup_data,
    mark_followup_sent,
    schedule_stale,
    get_due_stales,
    get_stale_data,
    cancel_stale,
)
from app.github.api import github_post, github_get
from app.nlp.lingo_client import translate
from app.settings import (
    FOLLOWUP_SCAN_INTERVAL_SECONDS,
    STALE_INTERVAL_HOURS,
    MAX_FOLLOWUP_ATTEMPTS,
)
from app.nlp.language_detect import detect_with_fallback

FOLLOWUP_TEMPLATE = (
    "Just a gentle follow-up on this issue.\n"
    "When you get a chance, could you please share an update on the progress?"
)

STALE_TEMPLATE = "No response received. Marking this as stale."


async def process_followup(key: str):
    data = get_followup_data(key)
    if not data or str(data.get("sent")) == "1" or "issue_number" not in data:
        return

    attempt = int(data.get("attempt", 1))
    if attempt > MAX_FOLLOWUP_ATTEMPTS:
        return  # silent stop

    repo = data["repo"]
    issue_number = int(data["issue_number"])
    assignee = data["assignee"]

    issue = await github_get(f"/repos/{repo}/issues/{issue_number}")

    # PR: ensure author is same
    if "pull_request" in issue:
        if issue["user"]["login"] != assignee:
            return
    else:
        assignees = [u["login"] for u in issue.get("assignees", [])]
        if assignee not in assignees:
            return

    # 🔒 Lock language from Redis, never re-detect from replies
    followup_lang = data.get("lang")
    if not followup_lang:
        title = issue.get("title", "")
        body = issue.get("body", "") or ""
        followup_lang = await detect_with_fallback(title, body)

    translated = await translate(FOLLOWUP_TEMPLATE, followup_lang)
    body = f"@{assignee}\n\n{translated}"

    await github_post(
        f"/repos/{repo}/issues/{issue_number}/comments",
        {"body": body}
    )

    mark_followup_sent(key)

    # Schedule stale for this attempt
    if attempt <= MAX_FOLLOWUP_ATTEMPTS:
        stale_at = time.time() + STALE_INTERVAL_HOURS * 3600
        schedule_stale(repo, issue_number, followup_lang, stale_at)


async def process_stale(key: str):
    data = get_stale_data(key)
    if not data or "issue_number" not in data:
        return

    repo = data["repo"]
    issue_number = int(data["issue_number"])
    lang = data.get("lang", "en")

    translated = await translate(STALE_TEMPLATE, lang)

    await github_post(
        f"/repos/{repo}/issues/{issue_number}/comments",
        {"body": translated + " 💤"}
    )

    await github_post(
        f"/repos/{repo}/issues/{issue_number}/labels",
        {"labels": ["stale"]}
    )

    cancel_stale(repo, issue_number)


async def followup_loop():
    while True:
        try:
            now = time.time()

            for key in get_due_followups(now):
                await process_followup(key)

            for key in get_due_stales(now):
                await process_stale(key)

        except Exception as e:
            print("Follow-up/Stale worker error:", e)

        await asyncio.sleep(FOLLOWUP_SCAN_INTERVAL_SECONDS)
