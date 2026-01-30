import asyncio
import time
from httpx import HTTPStatusError

from app.logger import get_logger
from app.cache.store import (
    get_due_followups,
    get_followup_data,
    mark_followup_sent,
    schedule_stale,
    get_due_stales,
    get_stale_data,
    cancel_stale,
    cancel_followup,
    has_followup,
    schedule_followup,
    mark_repo_installed,
    unmark_repo_installed,
    is_repo_installed,
    purge_orphaned_repos,
    mark_user_seen,  # ✅ NEW (critical fix)
)
from app.github.api import github_post, github_get
from app.nlp.lingo_client import translate
from app.settings import (
    FOLLOWUP_SCAN_INTERVAL_SECONDS,
    STALE_INTERVAL_HOURS,
    MAX_FOLLOWUP_ATTEMPTS,
)

logger = get_logger("yaplate.workers.followup")

FOLLOWUP_TEMPLATE = (
    "Just a gentle follow-up on this issue.\n"
    "When you get a chance, could you please share an update on the progress?"
)

STALE_TEMPLATE = "No response received. Marking this as stale."


# =========================================================
# Startup reconciliation
# =========================================================

async def reconcile_on_startup():
    """
    Rebuild authoritative state after downtime:
    - Mark installed repos
    - Seed follow-ups
    - Seed greeting state (critical fix)
    - Purge orphaned Redis state
    """
    try:
        result = await list_installed_repos()
        repos = result.get("repositories", [])
        now = time.time()

        installed = set()

        for repo_obj in repos:
            full = repo_obj.get("full_name")
            repo_id = repo_obj.get("id")

            if not full or repo_id is None:
                continue

            installed.add(full)
            mark_repo_installed(full)

            try:
                issues = await list_open_assigned_issues(full)
            except Exception:
                logger.exception("Failed to list assigned issues for %s", full)
                continue

            for issue in issues:
                number = issue.get("number")
                if number is None:
                    continue

                # --------------------------------------------------
                # ✅ Seed greeting state (BUG FIX)
                # --------------------------------------------------
                author = issue.get("user", {}).get("login")
                if author:
                    mark_user_seen(repo_id, author)

                assignees = issue.get("assignees", [])
                for a in assignees:
                    login = a.get("login")
                    if login:
                        mark_user_seen(repo_id, login)

                labels = [l.get("name", "").lower() for l in issue.get("labels", [])]

                if not assignees:
                    continue
                if "stale" in labels:
                    continue
                if has_followup(full, number):
                    continue

                assignee = assignees[0].get("login")
                if not assignee:
                    continue

                title = issue.get("title", "")
                body = issue.get("body") or ""

                lang = "en" if not body.strip() else await detect_with_fallback(title, body)
                due_at = now + FOLLOWUP_DEFAULT_INTERVAL_HOURS * 3600

                schedule_followup(
                    repo=full,
                    issue_number=number,
                    assignee=assignee,
                    lang=lang,
                    due_at=due_at,
                )

        purge_orphaned_repos(installed)

    except Exception:
        logger.exception("Startup reconciliation failed")


# =========================================================
# Follow-up processing
# =========================================================

async def process_followup(key: str):
    data = get_followup_data(key)
    if not data or str(data.get("sent")) == "1":
        return

    repo = data.get("repo")
    issue_number = data.get("issue_number")

    if not repo or issue_number is None:
        return

    issue_number = int(issue_number)

    if not is_repo_installed(repo):
        cancel_followup(repo, issue_number)
        cancel_stale(repo, issue_number)
        return

    attempt = int(data.get("attempt", 1))
    if attempt > MAX_FOLLOWUP_ATTEMPTS:
        return  # silent stop

    assignee = data.get("assignee")
    lang = data.get("lang", "en")

    # Safe fetch
    try:
        issue = await github_get(f"/repos/{repo}/issues/{issue_number}")
    except HTTPStatusError as e:
        if e.response.status_code == 404:
            cancel_followup(repo, issue_number)
            return
        raise

    labels = [l.get("name", "").lower() for l in issue.get("labels", [])]
    if "stale" in labels:
        cancel_followup(repo, issue_number)
        cancel_stale(repo, issue_number)
        return

    # Validate target
    if "pull_request" in issue:
        if issue.get("user", {}).get("login") != assignee:
            return
    else:
        assignees = [u.get("login") for u in issue.get("assignees", [])]
        if assignee not in assignees:
            return

    translated = await translate(FOLLOWUP_TEMPLATE, lang)
    body = f"@{assignee}\n\n{translated}"

    await github_post(
        f"/repos/{repo}/issues/{issue_number}/comments",
        {"body": body}
    )

    mark_followup_sent(key)

    stale_at = time.time() + STALE_INTERVAL_HOURS * 3600
    schedule_stale(repo, issue_number, lang, stale_at)


# =========================================================
# Stale processing
# =========================================================

async def process_stale(key: str):
    data = get_stale_data(key)
    if not data:
        return

    repo = data.get("repo")
    issue_number = data.get("issue_number")

    if not repo or issue_number is None:
        return

    issue_number = int(issue_number)

    if not is_repo_installed(repo):
        cancel_stale(repo, issue_number)
        cancel_followup(repo, issue_number)
        return

    lang = data.get("lang", "en")

    try:
        issue = await github_get(f"/repos/{repo}/issues/{issue_number}")
    except HTTPStatusError as e:
        if e.response.status_code == 404:
            cancel_stale(repo, issue_number)
            return
        raise

    labels = [l.get("name", "").lower() for l in issue.get("labels", [])]
    if "stale" in labels:
        cancel_stale(repo, issue_number)
        return

    translated = await translate(STALE_TEMPLATE, lang)

    await github_post(
        f"/repos/{repo}/issues/{issue_number}/comments",
        {"body": translated}
    )

    await github_post(
        f"/repos/{repo}/issues/{issue_number}/labels",
        {"labels": ["stale"]}
    )

    cancel_stale(repo, issue_number)


# =========================================================
# Main worker loop
# =========================================================

async def followup_loop():
    while True:
        try:
            now = time.time()

            for key in get_due_followups(now):
                await process_followup(key)

            for key in get_due_stales(now):
                await process_stale(key)

        except asyncio.CancelledError:
            logger.info("Follow-up scheduler cancelled")
            raise
        except Exception:
            logger.exception("Follow-up scheduler error")

        await asyncio.sleep(FOLLOWUP_SCAN_INTERVAL_SECONDS)
