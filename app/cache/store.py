import time
from app.cache.keys import FOLLOWUP_PREFIX, FOLLOWUP_INDEX, KEY_PREFIX, FIRST_ISSUE_PREFIX, FIRST_PR_PREFIX
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

def schedule_followup(repo: str, issue_number: int, assignee: str, lang: str, due_at: float):
    r = get_redis()
    key = f"{FOLLOWUP_PREFIX}{repo}:{issue_number}"
    r.hset(key, mapping={
        "repo": repo,
        "issue_number": issue_number,
        "assignee": assignee,
        "lang": lang,
        "due_at": due_at,
        "sent": 0,
    })
    r.zadd(FOLLOWUP_INDEX, {key: due_at})

def cancel_followup(repo: str, issue_number: int):
    r = get_redis()
    key = f"{FOLLOWUP_PREFIX}{repo}:{issue_number}"
    r.delete(key)
    r.zrem(FOLLOWUP_INDEX, key)

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


def has_been_greeted_pr(repo: str, username: str) -> bool:
    r = get_redis()
    return r.exists(f"{FIRST_PR_PREFIX}{repo}:{username}")

def mark_greeted_pr(repo: str, username: str):
    r = get_redis()
    r.set(f"{FIRST_PR_PREFIX}{repo}:{username}", 1)
