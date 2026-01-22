from app.github.api import github_post, github_patch
from app.commands.parser import parse_translate_command, parse_reply_command
from app.commands.translate import translate_and_format
from app.commands.reply import build_proxy_reply
from app.cache.store import set_comment_mapping, get_comment_mapping
from app.nlp.context_builder import build_reply_context

async def handle_comment(payload):
    action = payload.get("action")
    sender = payload["sender"]["login"]

    if sender.lower().endswith("[bot]") or sender.lower() == "yaplate-bot":
        return

    comment = payload["comment"]
    comment_id = comment["id"]
    comment_body = comment["body"]

    repo = payload["repository"]["full_name"]
    issue_number = payload["issue"]["number"]

    # 1) Try reply command
    reply_parsed = parse_reply_command(comment_body)
    if reply_parsed:
        ctx = build_reply_context(payload)
        final_reply = await build_proxy_reply(
            parent_text=reply_parsed["parent_text"],
            speaker_text=reply_parsed["speaker_text"],
            speaker_username=ctx["speaker_username"],
            target_lang=reply_parsed["target_lang"]
        )
    else:
        # 2) Fallback to translate
        parsed = parse_translate_command(comment_body)
        if not parsed:
            return

        final_reply = await translate_and_format(
            parsed["quoted_text"],
            target_lang=parsed["target_lang"],
            quoted_label=parsed.get("quoted_label"),
            user_message=comment_body
        )

    # === Redis-backed edit-own-reply logic ===
    if action == "created":
        response = await github_post(
            f"/repos/{repo}/issues/{issue_number}/comments",
            {"body": final_reply}
        )
        set_comment_mapping(comment_id, response["id"])

    elif action == "edited":
        bot_comment_id = get_comment_mapping(comment_id)
        if bot_comment_id:
            await github_patch(
                f"/repos/{repo}/issues/comments/{bot_comment_id}",
                {"body": final_reply}
            )
        else:
            response = await github_post(
                f"/repos/{repo}/issues/{issue_number}/comments",
                {"body": final_reply}
            )
            set_comment_mapping(comment_id, response["id"])
