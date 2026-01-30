import hmac
import hashlib
import os
from typing import Optional


def verify_signature(payload: bytes, signature: Optional[str]) -> bool:
    """
    Verify GitHub webhook signature using HMAC SHA-256.

    Returns False on any validation failure.
    """
    if not signature:
        return False

    secret = os.getenv("GITHUB_WEBHOOK_SECRET")
    if not secret:
        return False

    try:
        mac = hmac.new(
            secret.encode(),
            msg=payload,
            digestmod=hashlib.sha256,
        )
        expected = "sha256=" + mac.hexdigest()
        return hmac.compare_digest(expected, signature.strip())
    except Exception:
        # Never raise from signature verification
        return False
