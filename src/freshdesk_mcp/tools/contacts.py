from typing import Any, Optional, cast
from mcp.server.fastmcp import FastMCP

from freshdesk_mcp import client


def register(mcp: FastMCP) -> None:
    """Register contact management tools."""

    @mcp.tool()
    def list_contacts(page: int = 1, per_page: int = 30, email: Optional[str] = None) -> list[dict]:
        """List or look up Freshdesk contacts (customers).

        Args:
            page: Page number (1-indexed).
            per_page: Results per page (max 100).
            email: Optional exact email address to filter by.
        """
        params: dict[str, Any] = {"page": page, "per_page": min(per_page, 100)}
        if email:
            params["email"] = email
        with client._client() as c:
            return cast(list[dict], client._handle_response(c.get("/contacts", params=params)))

    @mcp.tool()
    def create_contact(name: str, email: str, phone: Optional[str] = None) -> dict:
        """Create a new Freshdesk contact.

        Args:
            name: Full name of the contact.
            email: Email address of the contact.
            phone: Optional phone number.
        """
        payload: dict[str, Any] = {"name": name, "email": email}
        if phone:
            payload["phone"] = phone
        with client._client() as c:
            return cast(dict, client._handle_response(c.post("/contacts", json=payload)))
