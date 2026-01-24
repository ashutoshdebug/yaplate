from app.github.comments import handle_comment
from app.commands.greet import greet_if_first_issue

async def handle_event(event_type: str, payload: dict):
    if event_type in ("issue_comment", "pull_request_review_comment"):
        await handle_comment(payload)

    elif event_type == "issues" and payload.get("action") == "opened":
        repo = payload["repository"]["full_name"]
        issue_number = payload["issue"]["number"]
        username = payload["issue"]["user"]["login"]

        await greet_if_first_issue(repo, issue_number, username)
