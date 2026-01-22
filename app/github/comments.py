from app.github.api import github_post
from app.commands.parser import parse_translate_command
from app.commands.translate import translate_and_format

async def handle_comment(payload):
    sender = payload["sender"]["login"]
    if sender.lower().endswith("[bot]") or sender.lower() == "yaplate-bot":
        return

    comment_body = payload["comment"]["body"]
    parsed = parse_translate_command(comment_body)

    if not parsed:
        return  # Bot not called, ignore

    repo = payload["repository"]["full_name"]
    issue_number = payload["issue"]["number"]

    translated_reply = await translate_and_format(
        parsed["quoted_text"],
        target_lang=parsed["target_lang"],
        user_message=comment_body
    )

    await github_post(
        f"/repos/{repo}/issues/{issue_number}/comments",
        {"body": translated_reply}
    )
