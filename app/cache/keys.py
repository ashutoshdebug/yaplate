# ---------------------------------------------------------
# Comment ↔ Bot reply mapping
# ---------------------------------------------------------

KEY_PREFIX = "yaplate:comment_map:"


# ---------------------------------------------------------
# Greeting tracking (repo-id safe)
# ---------------------------------------------------------

FIRST_ISSUE_PREFIX = "yaplate:first_issue_greeted:"
FIRST_PR_PREFIX = "yaplate:first_pr_greeted:"


# ---------------------------------------------------------
# Follow-up scheduling
# ---------------------------------------------------------

FOLLOWUP_PREFIX = "yaplate:followup:"
FOLLOWUP_INDEX = "yaplate:followup:index"


# ---------------------------------------------------------
# Stale issue handling
# ---------------------------------------------------------

STALE_PREFIX = "yaplate:stale:"
STALE_INDEX = "yaplate:stale:index"


# ---------------------------------------------------------
# Installation / repository lifecycle tracking (NEW)
# ---------------------------------------------------------
# These keys make Redis resilient to missed webhooks
# and bot restarts while offline.
# ---------------------------------------------------------

# Tracks repos that are currently installed for this app
# Key format:
#   yaplate:installed_repo:{owner}/{repo}
INSTALLED_REPO_PREFIX = "yaplate:installed_repo:"

# (Optional, future-proofing)
# Track installation ids if you later want multi-install isolation
# INSTALLATION_PREFIX = "yaplate:installation:"

FOLLOWUP_STOPPED_PREFIX = "yaplate:followup_stopped:"
