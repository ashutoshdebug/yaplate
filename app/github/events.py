from app.github.comments import handle_comment

async def handle_event(event_type: str, payload: dict):
    if event_type in ("issue_comment", "pull_request_review_comment"):
        await handle_comment(payload)
