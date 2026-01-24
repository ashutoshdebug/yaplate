from app.cache.redis_client import get_redis

KEY_PREFIX = "yaplate:comment_map:"

FIRST_ISSUE_PREFIX = "yaplate:first_issue_greeted:"

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
