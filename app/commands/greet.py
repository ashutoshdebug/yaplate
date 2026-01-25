from app.nlp.language_detect import detect_dominant_language
from app.nlp.lingo_client import translate
from app.github.api import github_post, get_user_issues
from app.cache.store import has_been_greeted, mark_greeted

BASE_WELCOME = """Hi @{user}, welcome to the project!

Thanks for opening your first issue here! We’re excited to have you contribute.

Here’s how you can contribute effectively:
- Read the README and contribution guidelines
- Provide minimal reproducible examples
- Add logs, screenshots, or steps to reproduce
- Feel free to ask if anything is unclear

We’re happy to have you here. Happy coding!
"""

async def greet_if_first_issue(repo, issue_number, username, title, body):
    if has_been_greeted(repo, username):
        return

    search = await get_user_issues(repo, username)
    if search.get("total_count", 0) == 1:
        lang = detect_dominant_language(title, body)

        message = BASE_WELCOME.format(user=username)

        if lang != "en":
            message = await translate(message, lang)

        await github_post(
            f"/repos/{repo}/issues/{issue_number}/comments",
            {"body": message}
        )

        mark_greeted(repo, username)
