from typing import Any, Optional, cast
from mcp.server.fastmcp import FastMCP

from freshdesk_mcp import client


def register(mcp: FastMCP) -> None:
    """Register contact management tools."""

    @mcp.tool()
    async def list_contacts(page: int = 1, per_page: int = 30, email: Optional[str] = None) -> list[dict]:
        """List or look up Freshdesk contacts (customers).

        Args:
            page: Page number (1-indexed).
            per_page: Results per page (max 100).
            email: Optional exact email address to filter by.
        """
        params: dict[str, Any] = {"page": page, "per_page": min(per_page, 100)}
        if email:
            params["email"] = email
        async with client._client() as c:
            return cast(list[dict], client._handle_response(await c.get("/contacts", params=params)))

    @mcp.tool()
    async def get_contact(contact_id: int) -> dict:
        """Get full details of a single Freshdesk contact by ID.

        Args:
            contact_id: The Freshdesk contact ID.
        """
        async with client._client() as c:
            return cast(dict, client._handle_response(await c.get(f"/contacts/{contact_id}")))

    @mcp.tool()
    async def create_contact(
        name: str,
        email: str,
        phone: Optional[str] = None,
        mobile: Optional[str] = None,
        company_id: Optional[int] = None,
    ) -> dict:
        """Create a new Freshdesk contact.

        Args:
            name: Full name of the contact.
            email: Email address of the contact.
            phone: Optional phone number.
            mobile: Optional mobile phone number.
            company_id: Optional Freshdesk company ID to associate with.
        """
        payload: dict[str, Any] = {"name": name, "email": email}
        if phone:
            payload["phone"] = phone
        if mobile:
            payload["mobile"] = mobile
        if company_id is not None:
            payload["company_id"] = company_id

        async with client._client() as c:
            return cast(dict, client._handle_response(await c.post("/contacts", json=payload)))

    @mcp.tool()
    async def update_contact(
        contact_id: int,
        name: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        mobile: Optional[str] = None,
        company_id: Optional[int] = None,
    ) -> dict:
        """Update an existing Freshdesk contact. Only provided fields are changed.

        Args:
            contact_id: The Freshdesk contact ID.
            name: Optional updated full name.
            email: Optional updated email address.
            phone: Optional updated phone number.
            mobile: Optional updated mobile phone number.
            company_id: Optional company ID to associate with.
        """
        payload: dict[str, Any] = {}
        if name is not None:
            payload["name"] = name
        if email is not None:
            payload["email"] = email
        if phone is not None:
            payload["phone"] = phone
        if mobile is not None:
            payload["mobile"] = mobile
        if company_id is not None:
            payload["company_id"] = company_id

        if not payload:
            raise ValueError("No fields provided to update.")

        async with client._client() as c:
            return cast(dict, client._handle_response(await c.put(f"/contacts/{contact_id}", json=payload)))

    @mcp.tool()
    async def delete_contact(contact_id: int) -> dict:
        """Delete (soft-delete) a Freshdesk contact by ID.

        Args:
            contact_id: The Freshdesk contact ID to delete.
        """
        async with client._client() as c:
            return cast(dict, client._handle_response(await c.delete(f"/contacts/{contact_id}")))

    @mcp.tool()
    async def search_contacts(query: str) -> list[dict]:
        """Search contacts using Freshdesk search query syntax (e.g. '"name:John"' or '"email:john@example.com"').

        Args:
            query: Freshdesk contact search query string.
        """
        async with client._client() as c:
            data = client._handle_response(await c.get("/search/contacts", params={"query": f'"{query}"'}))
        results = data.get("results", data) if isinstance(data, dict) else data
        return cast(list[dict], results)
