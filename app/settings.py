import os
from dotenv import load_dotenv

load_dotenv()

# === Raw environment values ===

GITHUB_WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET")

LINGO_API_KEY = os.getenv("LINGO_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# GitHub App authentication
GITHUB_APP_ID = os.getenv("GITHUB_APP_ID")
GITHUB_PRIVATE_KEY_PATH = os.getenv("GITHUB_PRIVATE_KEY_PATH")

# Follow-up configuration
FOLLOWUP_ENABLED = os.getenv("FOLLOWUP_ENABLED", "true").lower() == "true"
FOLLOWUP_DEFAULT_INTERVAL_HOURS = float(
    os.getenv("FOLLOWUP_DEFAULT_INTERVAL_HOURS", "48")
)
FOLLOWUP_SCAN_INTERVAL_SECONDS = float(
    os.getenv("FOLLOWUP_SCAN_INTERVAL_SECONDS", "600")
)
STALE_INTERVAL_HOURS = float(os.getenv("STALE_INTERVAL_HOURS", "72"))

MAX_FOLLOWUP_ATTEMPTS = int(os.getenv("MAX_FOLLOWUP_ATTEMPTS", "3"))

# Configurable messages

FALLBACK_MESSAGE_TEMPLATE =  "LLM service is temporarily unavailable. Please try again later."

ISSUE_WELCOME_MESSAGE = """Hi @{user}, welcome to the project!

Thanks for opening your first issue here. We really appreciate you taking the time to report this.

To help us resolve it faster:
- Add clear reproduction steps
- Share logs, screenshots, or error messages
- Mention expected vs actual behavior
- Custom message issue

Feel free to ask if anything is unclear. Happy collaborating!
"""

PR_WELCOME_MESSAGE = """Hi @{user}, welcome to the project!

Thanks for opening your first pull request — great to see your contribution!

A few tips for a smooth review:
- Make sure tests pass
- Keep commits focused and well-described
- Add context if the change is large
- Custom message PR

Looking forward to reviewing your work. Happy coding!
"""

FOLLOWUP_ISSUE_MESSAGE = (
    "Just a gentle follow-up on this issue.\n"
    "When you get a chance, could you please share an update on the progress?"
)

FOLLOWUP_PR_MESSAGE = (
    "Just a gentle follow-up on this PR.\n"
    "When you get a chance, could you please share an update on the progress?"
)

STALE_MESSAGE = "No response received. Marking this as stale."

STOPPING_ESCALATION_MAINTAINERS = (
    "The author indicated they are blocked or waiting for "
    "maintainer action. Follow-up reminders have been paused."
)

STOPPING_ESCALATION_HARD_STOP = (
    "The author replied only with a quoted message, "
    "indicating no further automated follow-ups are needed."
)


def validate_llm_settings() -> None:
    """
    Validate required LLM configuration.

    Raises RuntimeError if required keys are missing.
    """
    if not LINGO_API_KEY:
        raise RuntimeError("LINGO_API_KEY is not set")

    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is not set")


def validate_github_settings() -> None:
    """
    Validate required GitHub App configuration.

    Raises RuntimeError if required values are missing or invalid.
    """
    if not GITHUB_APP_ID:
        raise RuntimeError("GITHUB_APP_ID is not set")

    if not GITHUB_PRIVATE_KEY_PATH:
        raise RuntimeError("GITHUB_PRIVATE_KEY_PATH is not set")

    if not os.path.exists(GITHUB_PRIVATE_KEY_PATH):
        raise RuntimeError(
            f"GITHUB_PRIVATE_KEY_PATH does not exist: {GITHUB_PRIVATE_KEY_PATH}"
        )
