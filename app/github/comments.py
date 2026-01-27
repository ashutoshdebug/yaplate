from app.github.api import github_post, github_patch, github_delete, get_repo_maintainers
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
    cancel_followup,
    cancel_stale,
    reschedule_followup,
    get_followup_data,
)
from app.settings import FOLLOWUP_DEFAULT_INTERVAL_HOURS, MAX_FOLLOWUP_ATTEMPTS
from app.nlp.context_builder import build_reply_context
from app.nlp.semantic_check import wants_maintainer_attention
import asyncio
import time


def is_pure_quote(comment_body: str) -> bool:
    lines = [l.strip() for l in comment_body.strip().splitlines()]
    return lines and all(line.startswith(">") for line in lines)

def extract_user_text(comment_body: str) -> str:
    return "\n".join(
        line for line in comment_body.splitlines()
        if not line.strip().startswith(">")
    ).strip()


async def handle_comment(payload):
    action = payload.get("action")

    comment = payload["comment"]
    comment_id = comment["id"]
    comment_body = comment.get("body", "")
    comment_user = comment["user"]["login"]

    if comment_user.lower().endswith("[bot]") or comment_user.lower() == "yaplate-bot":
        return

    repo = payload["repository"]["full_name"]
    issue_number = payload["issue"]["number"]

    # 1. Hard stop: pure quote
    if action == "created" and is_pure_quote(comment_body):
        cancel_followup(repo, issue_number)
        cancel_stale(repo, issue_number)
        return

    # 2. Quote + text → check for maintainer intent
    if action == "created" and comment_body.lstrip().startswith(">"):
        user_text = extract_user_text(comment_body)

        if user_text and await wants_maintainer_attention(user_text):
            maintainers = await get_repo_maintainers(repo)
            if maintainers:
                mentions = " ".join(f"@{m}" for m in maintainers)
                await github_post(
                    f"/repos/{repo}/issues/{issue_number}/comments",
                    {
                        "body": f"{mentions}\n\nThe author is waiting for maintainer / reviewer approval. Escalating and stopping automation."
                    }
                )

            # HARD STOP: no more followups or stale
            cancel_followup(repo, issue_number)
            cancel_stale(repo, issue_number)
            return

    # 3. Normal reply → reset follow-up cycle
    if action == "created":
        cancel_stale(repo, issue_number)

        key = f"yaplate:followup:{repo}:{issue_number}"
        data = get_followup_data(key)

        if data:
            attempt = int(data.get("attempt", 1))
            if attempt < MAX_FOLLOWUP_ATTEMPTS:
                next_due = time.time() + FOLLOWUP_DEFAULT_INTERVAL_HOURS * 3600
                reschedule_followup(repo, issue_number, next_due)
            else:
                cancel_followup(repo, issue_number)

    # 4. Handle user comment deletion
    if action == "deleted":
        await asyncio.sleep(1.5)
        bot_comment_id = get_comment_mapping(comment_id)
        if bot_comment_id:
            try:
                await github_delete(f"/repos/{repo}/issues/comments/{bot_comment_id}")
            except Exception:
                pass
            delete_comment_mapping(comment_id)
        return

    # 5. Parse commands
    summarize_parsed = parse_summarize_command(comment_body)
    reply_parsed = parse_reply_command(comment_body)
    translate_parsed = parse_translate_command(comment_body)

    if action == "edited" and not (summarize_parsed or reply_parsed or translate_parsed):
        return

    if summarize_parsed:
        final_reply = await summarize_thread(
            repo=repo,
            issue_number=issue_number,
            target_lang=summarize_parsed["target_lang"],
            trigger_text=comment_body,
        )

    elif reply_parsed:
        ctx = build_reply_context(payload)
        final_reply = await build_proxy_reply(
            parent_text=reply_parsed["parent_text"],
            speaker_text=reply_parsed["speaker_text"],
            speaker_username=ctx["speaker_username"],
            target_lang=reply_parsed["target_lang"],
        )

    elif translate_parsed:
        final_reply = await translate_and_format(
            translate_parsed["quoted_text"],
            target_lang=translate_parsed["target_lang"],
            quoted_label=translate_parsed.get("quoted_label"),
            user_message=comment_body,
        )
    else:
        return

    # 6. Redis-backed reply mapping
    if action == "created":
        await asyncio.sleep(1.5)
        response = await github_post(
            f"/repos/{repo}/issues/{issue_number}/comments",
            {"body": final_reply},
        )
        set_comment_mapping(comment_id, response["id"])

    elif action == "edited":
        bot_comment_id = get_comment_mapping(comment_id)
        await asyncio.sleep(1.5)

        if bot_comment_id:
            await github_patch(
                f"/repos/{repo}/issues/comments/{bot_comment_id}",
                {"body": final_reply},
            )
        else:
            response = await github_post(
                f"/repos/{repo}/issues/{issue_number}/comments",
                {"body": final_reply},
            )
            set_comment_mapping(comment_id, response["id"])
