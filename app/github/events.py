from app.github.comments import handle_comment
from app.commands.greet import greet_if_first_issue, greet_if_first_pr
from app.cache.store import schedule_followup, cancel_followup
from app.nlp.language_detect import detect_with_fallback
from app.settings import FOLLOWUP_DEFAULT_INTERVAL_HOURS
import time


async def handle_event(event_type: str, payload: dict):
    # ---------------- COMMENTS ----------------
    if "repository" not in payload:
        return
    
    if event_type in ("issue_comment", "pull_request_review_comment"):
        await handle_comment(payload)
        return

    repo = payload["repository"]["full_name"]

    # ---------------- ISSUES ----------------
    if event_type == "issues":
        action = payload.get("action")
        issue = payload["issue"]
        issue_number = issue["number"]
        title = issue["title"]
        body = issue["body"] or ""

        if action == "opened":
            username = issue["user"]["login"]
            await greet_if_first_issue(repo, issue_number, username, title, body)

        elif action == "assigned":
            assignee = payload["assignee"]["login"]
            lang = await detect_with_fallback(title, body)
            due_at = time.time() + FOLLOWUP_DEFAULT_INTERVAL_HOURS * 3600

            schedule_followup(
                repo=repo,
                issue_number=issue_number,
                assignee=assignee,
                lang=lang,
                due_at=due_at,
            )

        elif action in ("unassigned", "closed"):
            cancel_followup(repo, issue_number)

    # ---------------- PULL REQUESTS ----------------
    elif event_type == "pull_request":
        action = payload.get("action")
        pr = payload["pull_request"]
        pr_number = pr["number"]
        title = pr["title"]
        body = pr["body"] or ""
        author = pr["user"]["login"]

        if action == "opened":
            await greet_if_first_pr(repo, pr_number, author, title, body)

            lang = await detect_with_fallback(title, body)
            due_at = time.time() + FOLLOWUP_DEFAULT_INTERVAL_HOURS * 3600

            schedule_followup(
                repo=repo,
                issue_number=pr_number,
                assignee=author,  # reused field for worker
                lang=lang,
                due_at=due_at,
            )

        elif action == "closed":
            cancel_followup(repo, pr_number)
