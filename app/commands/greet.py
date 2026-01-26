from app.nlp.language_detect import detect_with_fallback
from app.nlp.lingo_client import translate
from app.github.api import github_post
from app.cache.store import (
    has_been_greeted,
    mark_greeted,
    has_been_greeted_pr,
    mark_greeted_pr,
)

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

async def greet_if_first_issue(repo, issue_number, username, title, body):
    if has_been_greeted(repo, username):
        return
    await _send_greeting(repo, issue_number, username, title, body, ISSUE_WELCOME)
    mark_greeted(repo, username)

async def greet_if_first_pr(repo, pr_number, username, title, body):
    if has_been_greeted_pr(repo, username):
        return
    await _send_greeting(repo, pr_number, username, title, body, PR_WELCOME)
    mark_greeted_pr(repo, username)

async def _send_greeting(repo, number, username, title, body, template):
    lang = await detect_with_fallback(title, body)

    if not isinstance(lang, str) or len(lang) != 2:
        lang = "en"

    message = template.format(user=username)

    if lang != "en":
        message = await translate(message, lang)

    await github_post(
        f"/repos/{repo}/issues/{number}/comments",
        {"body": message}
    )
