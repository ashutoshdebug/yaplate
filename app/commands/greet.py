from app.github.api import github_post, get_user_issues
from app.cache.store import has_been_greeted, mark_greeted

WELCOME_MESSAGE = """👋 Hi @{user}, welcome to the project!

Thanks for opening your first issue here 🎉

Here’s how you can contribute effectively:
- 📖 Read the README and contribution guidelines
- 🐛 Provide minimal reproducible examples
- 🧪 Add logs, screenshots, or steps to reproduce
- 💡 Feel free to ask if anything is unclear

We’re happy to have you here. 🚀
"""

async def greet_if_first_issue(repo: str, issue_number: int, username: str):
    if has_been_greeted(repo, username):
        return

    search = await get_user_issues(repo, username)
    total = search.get("total_count", 0)

    if total == 1:  # This is their first issue in this repo
        body = WELCOME_MESSAGE.format(user=username)
        await github_post(f"/repos/{repo}/issues/{issue_number}/comments", {"body": body})
        mark_greeted(repo, username)
