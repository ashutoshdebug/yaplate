import asyncio

from app.logger import get_logger
from app.nlp.language_detect import detect_with_fallback
from app.nlp.lingo_client import translate
from app.github.api import github_post
from app.cache.store import (
    has_been_greeted,
    mark_greeted,
    has_been_greeted_pr,
    mark_greeted_pr,
)


logger = get_logger("yaplate.commands.greet")


ISSUE_WELCOME = """Hi @{user}, welcome to the project!

Thanks for opening your first issue here. We really appreciate you taking the time to report this.

To help us resolve it faster:
- Add clear reproduction steps
- Share logs, screenshots, or error messages
- Mention expected vs actual behavior

Feel free to ask if anything is unclear. Happy collaborating!
"""

PR_WELCOME = """Hi @{user}, welcome to the project!

Thanks for opening your first pull request — great to see your contribution!

A few tips for a smooth review:
- Make sure tests pass
- Keep commits focused and well-described
- Add context if the change is large

Looking forward to reviewing your work. Happy coding!
"""


async def greet_if_first_issue(repo_id, repo_full_name, issue_number, username, title, body):
    if has_been_greeted(repo_id, username):
        return

    try:
        await _send_greeting(
            repo_full_name,
            issue_number,
            username,
            title,
            body,
            ISSUE_WELCOME,
        )
    except RepoUnavailable:
        logger.warning("Repo unavailable during issue greeting: %s", repo_full_name)
        unmark_repo_installed(repo_full_name)
        return

    mark_greeted(repo_id, username)


async def greet_if_first_pr(repo_id, repo_full_name, pr_number, username, title, body):
    if has_been_greeted_pr(repo_id, username):
        return

    try:
        await _send_greeting(
            repo_full_name,
            pr_number,
            username,
            title,
            body,
            PR_WELCOME,
        )
    except RepoUnavailable:
        logger.warning("Repo unavailable during PR greeting: %s", repo_full_name)
        unmark_repo_installed(repo_full_name)
        return

    mark_greeted_pr(repo_id, username)


# ---------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------

async def _send_greeting(
    repo_full_name: str,
    number: int,
    username: str,
    title: str,
    body: str,
    template: str,
):
    # Normalize inputs defensively
    username = username or ""
    title = title or ""
    body = body or ""

    # Small delay to avoid racing GitHub UI
    await asyncio.sleep(2)

    lang = await detect_with_fallback(title, body)
    if not isinstance(lang, str) or len(lang) != 2:
        lang = "en"

    message = template.format(user=username)

    if lang != "en":
        message = await translate(message, lang)

    await github_post(
        f"/repos/{repo_full_name}/issues/{number}/comments",
        {"body": message}
    )
