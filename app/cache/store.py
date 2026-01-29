import time
from app.cache.keys import (
    FOLLOWUP_PREFIX, FOLLOWUP_INDEX, KEY_PREFIX,
    FIRST_ISSUE_PREFIX, FIRST_PR_PREFIX,
    STALE_PREFIX, STALE_INDEX
)
from app.cache.redis_client import get_redis


def set_comment_mapping(user_comment_id: int, bot_comment_id: int):
    r = get_redis()
    r.set(f"{KEY_PREFIX}{user_comment_id}", bot_comment_id)

def get_comment_mapping(user_comment_id: int):
    r = get_redis()
    return r.get(f"{KEY_PREFIX}{user_comment_id}")

def delete_comment_mapping(user_comment_id: int):
    r = get_redis()
    r.delete(f"{KEY_PREFIX}{user_comment_id}")

def has_been_greeted(repo: str, username: str) -> bool:
    r = get_redis()
    return r.exists(f"{FIRST_ISSUE_PREFIX}{repo}:{username}")

def mark_greeted(repo: str, username: str):
    r = get_redis()
    r.set(f"{FIRST_ISSUE_PREFIX}{repo}:{username}", 1)


# ---------------- FOLLOWUP ----------------

def schedule_followup(repo: str, issue_number: int, assignee: str, lang: str, due_at: float, attempt: int = 1):
    r = get_redis()
    key = f"{FOLLOWUP_PREFIX}{repo}:{issue_number}"
    r.hset(key, mapping={
        "repo": repo,
        "issue_number": issue_number,
        "assignee": assignee,
        "lang": lang,
        "due_at": due_at,
        "sent": 0,
        "attempt": attempt,
    })
    r.zadd(FOLLOWUP_INDEX, {key: due_at})

def reschedule_followup(repo: str, issue_number: int, next_due_at: float):
    """
    Increase attempt counter and reschedule follow-up.
    """
    r = get_redis()
    key = f"{FOLLOWUP_PREFIX}{repo}:{issue_number}"
    data = r.hgetall(key)

    if not data:
        return

    attempt = int(data.get("attempt", 1)) + 1

    r.hset(key, mapping={
        "due_at": next_due_at,
        "sent": 0,
        "attempt": attempt,
    })
    r.zadd(FOLLOWUP_INDEX, {key: next_due_at})

def cancel_followup(repo: str, issue_number: int):
    r = get_redis()
    key = f"{FOLLOWUP_PREFIX}{repo}:{issue_number}"

    # Remove followup state
    r.delete(key)

    # Remove from scheduler queue
    r.zrem(FOLLOWUP_INDEX, key)

    # Safety: remove any stale job too
    stale_key = f"{STALE_PREFIX}{repo}:{issue_number}"
    r.delete(stale_key)
    r.zrem(STALE_INDEX, stale_key)

def get_due_followups(now: float):
    r = get_redis()
    return r.zrangebyscore(FOLLOWUP_INDEX, 0, now)

def mark_followup_sent(key: str):
    r = get_redis()
    r.hset(key, "sent", 1)
    r.zrem(FOLLOWUP_INDEX, key)

def get_followup_data(key: str):
    r = get_redis()
    return r.hgetall(key)


# ---------------- GREET ----------------

# ---------------- GREET (rename-safe using repo_id) ----------------

def has_been_greeted(repo_id: int, username: str) -> bool:
    r = get_redis()
    return r.exists(f"{FIRST_ISSUE_PREFIX}{repo_id}:{username}")

def mark_greeted(repo_id: int, username: str):
    r = get_redis()
    r.set(f"{FIRST_ISSUE_PREFIX}{repo_id}:{username}", 1)

def has_been_greeted_pr(repo_id: int, username: str) -> bool:
    r = get_redis()
    return r.exists(f"{FIRST_PR_PREFIX}{repo_id}:{username}")

def mark_greeted_pr(repo_id: int, username: str):
    r = get_redis()
    r.set(f"{FIRST_PR_PREFIX}{repo_id}:{username}", 1)



# ---------------- STALE ----------------

def schedule_stale(repo: str, issue_number: int, lang: str, due_at: float):
    r = get_redis()
    key = f"{STALE_PREFIX}{repo}:{issue_number}"
    r.hset(key, mapping={
        "repo": repo,
        "issue_number": issue_number,
        "lang": lang,
        "due_at": due_at,
    })
    r.zadd(STALE_INDEX, {key: due_at})

def cancel_stale(repo: str, issue_number: int):
    r = get_redis()
    key = f"{STALE_PREFIX}{repo}:{issue_number}"
    r.delete(key)
    r.zrem(STALE_INDEX, key)

def get_due_stales(now: float):
    r = get_redis()
    return r.zrangebyscore(STALE_INDEX, 0, now)

def get_stale_data(key: str):
    r = get_redis()
    return r.hgetall(key)
