from app.github.api import github_post, github_patch, github_delete
from app.commands.summarize import summarize_thread
from app.commands.parser import (
    parse_summarize_command,
    parse_translate_command,
    parse_reply_command,
)
from app.commands.translate import translate_and_format
from app.commands.reply import build_proxy_reply
from app.cache.store import (
    set_comment_mapping,
    get_comment_mapping,
    delete_comment_mapping,
)
import asyncio
from app.nlp.context_builder import build_reply_context


async def handle_comment(payload):
    action = payload.get("action")

    comment = payload["comment"]
    comment_id = comment["id"]
    comment_body = comment.get("body", "")
    comment_user = comment["user"]["login"]

    sender = payload["sender"]["login"]

    # Ignore all bot authored events completely (prevents self-delete loops)
    if comment_user.lower().endswith("[bot]") or comment_user.lower() == "yaplate-bot":
        return

    repo = payload["repository"]["full_name"]
    issue_number = payload["issue"]["number"]

    # === DELETE HANDLING ===
    # If user deletes their comment, delete bot's mapped reply
    if action == "deleted":
        await asyncio.sleep(1.5)
        bot_comment_id = get_comment_mapping(comment_id)
        if bot_comment_id:
            try:
                await github_delete(f"/repos/{repo}/issues/comments/{bot_comment_id}")
            except Exception:
                # Bot comment may already be gone; never crash webhook
                pass
            delete_comment_mapping(comment_id)
        return

    # Parse all possible commands
    trigger_text = comment_body
    summarize_parsed = parse_summarize_command(comment_body)
    reply_parsed = parse_reply_command(comment_body)
    # print("RAW COMMENT BODY:\n", comment_body)
    translate_parsed = parse_translate_command(comment_body)
    # print("PARSED TRANSLATE:", translate_parsed)

    # If edited and command removed, do nothing (leave old bot reply)
    if action == "edited" and not (summarize_parsed or reply_parsed or translate_parsed):
        return

    # 0) Summarize
    if summarize_parsed:
        final_reply = await summarize_thread(
            repo=repo,
            issue_number=issue_number,
            target_lang=summarize_parsed["target_lang"],
            trigger_text=trigger_text,
        )

    # 1) Proxy reply
    elif reply_parsed:
        ctx = build_reply_context(payload)
        final_reply = await build_proxy_reply(
            parent_text=reply_parsed["parent_text"],
            speaker_text=reply_parsed["speaker_text"],
            speaker_username=ctx["speaker_username"],
            target_lang=reply_parsed["target_lang"],
        )

    # 2) Translate
    elif translate_parsed:
        final_reply = await translate_and_format(
            translate_parsed["quoted_text"],
            target_lang=translate_parsed["target_lang"],
            quoted_label=translate_parsed.get("quoted_label"),
            user_message=comment_body,
        )

    else:
        return

    # === Redis-backed edit-own-reply logic ===
    if action == "created":
        await asyncio.sleep(1.5)
        response = await github_post(
            f"/repos/{repo}/issues/{issue_number}/comments",
            {"body": final_reply},
        )
        set_comment_mapping(comment_id, response["id"])

    elif action == "edited":
        bot_comment_id = get_comment_mapping(comment_id)
        if bot_comment_id:
            await asyncio.sleep(1.5)
            await github_patch(
                f"/repos/{repo}/issues/comments/{bot_comment_id}",
                {"body": final_reply},
            )
        else:
            await asyncio.sleep(1.5)
            response = await github_post(
                f"/repos/{repo}/issues/{issue_number}/comments",
                {"body": final_reply},
            )
            set_comment_mapping(comment_id, response["id"])
