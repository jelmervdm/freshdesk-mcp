import logging
import os
import sys
from typing import Any, cast

import httpx

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

FRESHDESK_DOMAIN = os.environ.get("FRESHDESK_DOMAIN")
FRESHDESK_API_KEY = os.environ.get("FRESHDESK_API_KEY")

if not FRESHDESK_DOMAIN or not FRESHDESK_API_KEY:
    print(
        "ERROR: FRESHDESK_DOMAIN and FRESHDESK_API_KEY environment variables " "must be set before starting this server.",
        file=sys.stderr,
    )

BASE_URL = f"https://{FRESHDESK_DOMAIN}.freshdesk.com/api/v2" if FRESHDESK_DOMAIN else None


# ---------------------------------------------------------------------------
# Human-readable <-> Freshdesk enum mappings
# ---------------------------------------------------------------------------

PRIORITY_MAP = {"low": 1, "medium": 2, "high": 3, "urgent": 4}
STATUS_MAP = {"open": 2, "pending": 3, "resolved": 4, "closed": 5}
SOURCE_MAP = {
    "email": 1,
    "portal": 2,
    "phone": 3,
    "chat": 7,
    "feedback_widget": 9,
    "outbound_email": 10,
}

STATUS_MAP_REV = {v: k for k, v in STATUS_MAP.items()}
PRIORITY_MAP_REV = {v: k for k, v in PRIORITY_MAP.items()}


def _client() -> httpx.Client:
    if not BASE_URL or not FRESHDESK_API_KEY:
        raise RuntimeError("Freshdesk is not configured. Set FRESHDESK_DOMAIN and " "FRESHDESK_API_KEY environment variables.")
    return httpx.Client(
        base_url=BASE_URL,
        auth=(FRESHDESK_API_KEY, "X"),
        headers={"Content-Type": "application/json"},
        timeout=30.0,
    )


def _handle_response(resp: httpx.Response) -> Any:
    if resp.status_code >= 400:
        try:
            detail = resp.json()
        except Exception:
            detail = resp.text
        raise RuntimeError(f"Freshdesk API error {resp.status_code}: {detail}")
    if resp.status_code == 204 or not resp.content:
        return {"success": True}
    return resp.json()


def _simplify_ticket(t: dict) -> dict:
    """Return a compact, human-readable summary of a ticket."""
    return {
        "id": t.get("id"),
        "subject": t.get("subject"),
        "status": STATUS_MAP_REV.get(cast(int, t.get("status")), t.get("status")),
        "priority": PRIORITY_MAP_REV.get(cast(int, t.get("priority")), t.get("priority")),
        "requester_id": t.get("requester_id"),
        "responder_id": t.get("responder_id"),
        "created_at": t.get("created_at"),
        "updated_at": t.get("updated_at"),
        "tags": t.get("tags"),
        "type": t.get("type"),
    }
