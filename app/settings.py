import os
from dotenv import load_dotenv

load_dotenv()

GITHUB_WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET")
LINGO_API_KEY = os.getenv("LINGO_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not LINGO_API_KEY:
    raise RuntimeError("LINGO_API_KEY is not set")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not set")

# GitHub App authentication
GITHUB_APP_ID = os.getenv("GITHUB_APP_ID")
GITHUB_PRIVATE_KEY_PATH = os.getenv("GITHUB_PRIVATE_KEY_PATH")

FOLLOWUP_ENABLED = os.getenv("FOLLOWUP_ENABLED", "true").lower() == "true"
FOLLOWUP_DEFAULT_INTERVAL_HOURS = float(os.getenv("FOLLOWUP_DEFAULT_INTERVAL_HOURS", "48"))  # ~18 seconds
FOLLOWUP_SCAN_INTERVAL_SECONDS = float(os.getenv("FOLLOWUP_SCAN_INTERVAL_SECONDS", "600"))  # for fast testing
STALE_INTERVAL_HOURS = float(os.getenv("STALE_INTERVAL_HOURS", "72"))
