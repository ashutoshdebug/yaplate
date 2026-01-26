import asyncio
import time
from app.cache.store import get_due_followups, get_followup_data, mark_followup_sent
from app.github.api import github_post, github_get
from app.nlp.lingo_client import translate
from app.settings import FOLLOWUP_SCAN_INTERVAL_SECONDS
from app.nlp.language_detect import detect_with_fallback
FOLLOWUP_TEMPLATE = (
    "Just a gentle follow-up on this issue.\n"
    "When you get a chance, could you please share an update on the progress?"
)

async def process_followup(key: str):
    data = get_followup_data(key)
    if not data or str(data.get("sent")) == "1":
        return

    repo = data["repo"]
    issue_number = int(data["issue_number"])
    assignee = data["assignee"]
    issue_lang = data["lang"]  # fallback

    issue = await github_get(f"/repos/{repo}/issues/{issue_number}")

    # If it's a PR, the target user is the author
    if "pull_request" in issue:
        if issue["user"]["login"] != assignee:
            return
    else:
        # Normal issue: target user must still be an assignee
        current_assignees = [u["login"] for u in issue.get("assignees", [])]
        if assignee not in current_assignees:
            return
    followup_lang = issue_lang

    try:
        comments = await github_get(f"/repos/{repo}/issues/{issue_number}/comments")
        for c in comments:
            if c["user"]["login"] == assignee and c.get("body", "").strip():
                followup_lang = await detect_with_fallback("Assignee comment", c["body"])
                break
    except Exception:
        pass

    translated = await translate(FOLLOWUP_TEMPLATE, followup_lang)
    body = f"@{assignee}\n\n{translated}"

    await github_post(
        f"/repos/{repo}/issues/{issue_number}/comments",
        {"body": body}
    )

    mark_followup_sent(key)

async def followup_loop():
    while True:
        try:
            now = time.time()
            due_keys = get_due_followups(now)

            for key in due_keys:
                await process_followup(key)

        except Exception as e:
            print("Follow-up worker error:", e)

        await asyncio.sleep(FOLLOWUP_SCAN_INTERVAL_SECONDS)
