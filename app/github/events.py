from app.github.comments import handle_comment
from app.commands.greet import greet_if_first_issue, greet_if_first_pr
from app.cache.store import schedule_followup, cancel_followup, cancel_stale
from app.nlp.language_detect import detect_with_fallback
from app.settings import FOLLOWUP_DEFAULT_INTERVAL_HOURS
import time


async def handle_event(event_type: str, payload: dict):
    # ---------------- COMMENTS ----------------
    if "repository" not in payload:
        return

    repo_full = payload["repository"]["full_name"]
    repo_id = payload["repository"]["id"]

    # ---------------------------------------------------------
    # 5. Comment events
    # ---------------------------------------------------------
    if event_type in ("issue_comment", "pull_request_review_comment"):
        try:
            await handle_comment(payload)
        except RepoUnavailable:
            issue = payload.get("issue")
            if issue:
                cancel_followup(repo_full, issue["number"])
                cancel_stale(repo_full, issue["number"])
        return

    repo = payload["repository"]["full_name"]

    # ---------------- ISSUES ----------------
    if event_type == "issues":
        action = payload.get("action")
        issue = payload["issue"]
        issue_number = issue["number"]
        title = issue["title"]
        body = issue["body"] or ""

        try:
            if action == "opened":
                username = issue["user"]["login"]
                await greet_if_first_issue(repo_id, repo_full, issue_number, username, title, body)

        elif action == "assigned":
            assignee = payload["assignee"]["login"]
            lang = await detect_with_fallback(title, body)
            due_at = time.time() + FOLLOWUP_DEFAULT_INTERVAL_HOURS * 3600

                schedule_followup(
                    repo=repo_full,
                    issue_number=issue_number,
                    assignee=assignee,
                    lang=lang,
                    due_at=due_at,
                )

            elif action in ("unassigned", "closed", "deleted"):
                cancel_followup(repo_full, issue_number)
                cancel_stale(repo_full, issue_number)

        except RepoUnavailable:
            cancel_followup(repo_full, issue_number)
            cancel_stale(repo_full, issue_number)
        return

    # ---------------- PULL REQUESTS ----------------
    elif event_type == "pull_request":
        action = payload.get("action")
        pr = payload["pull_request"]
        pr_number = pr["number"]
        title = pr["title"]
        body = pr["body"] or ""
        author = pr["user"]["login"]

        try:
            if action == "opened":
                await greet_if_first_pr(repo_id, repo_full, pr_number, author, title, body)

            lang = await detect_with_fallback(title, body)
            due_at = time.time() + FOLLOWUP_DEFAULT_INTERVAL_HOURS * 3600

                schedule_followup(
                    repo=repo_full,
                    issue_number=pr_number,
                    assignee=author,
                    lang=lang,
                    due_at=due_at,
                )

            elif action in ("closed", "converted_to_draft"):
                cancel_followup(repo_full, pr_number)
                cancel_stale(repo_full, pr_number)

        except RepoUnavailable:
            cancel_followup(repo_full, pr_number)
            cancel_stale(repo_full, pr_number)
        return
