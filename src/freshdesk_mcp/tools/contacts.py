from typing import Annotated, Any, Optional, cast
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from freshdesk_mcp import client


def register(mcp: FastMCP) -> None:
    """Register contact management tools."""

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def list_contacts(
        page: Annotated[int, Field(description="Page number (1-indexed).")] = 1,
        per_page: Annotated[int, Field(description="Results per page (max 100).")] = 30,
        email: Annotated[Optional[str], Field(description="Optional exact email filter.")] = None,
    ) -> list[dict]:
        """List or look up Freshdesk contacts (customers).

        Use when browsing contacts sequentially or filtering by exact email.
        To search contacts by query syntax (e.g. name or domain), use search_contacts.
        To fetch full details for a single contact ID, use get_contact.

        Args:
            page: Page number (1-indexed).
            per_page: Results per page (max 100).
            email: Optional exact email address to filter by.
        """
        params: dict[str, Any] = {"page": page, "per_page": min(per_page, 100)}
        if email:
            params["email"] = email
        async with client._client() as c:
            return cast(
                list[dict], client._handle_response(await c.get("/contacts", params=params))
            )

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def get_contact(
        contact_id: Annotated[int, Field(description="The Freshdesk contact ID.")]
    ) -> dict:
        """Get full details of a single Freshdesk contact by ID.

        Use when looking up specific details for a known contact ID.
        To search contacts by name or email, use search_contacts or list_contacts.

        Args:
            contact_id: The Freshdesk contact ID.
        """
        async with client._client() as c:
            return cast(dict, client._handle_response(await c.get(f"/contacts/{contact_id}")))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=False))
    async def create_contact(
        name: Annotated[str, Field(description="Full name of the contact.")],
        email: Annotated[str, Field(description="Email address of the contact.")],
        phone: Annotated[Optional[str], Field(description="Optional landline phone number.")] = None,
        mobile: Annotated[Optional[str], Field(description="Optional mobile phone number.")] = None,
        company_id: Annotated[
            Optional[int], Field(description="Optional company ID association.")
        ] = None,
    ) -> dict:
        """Create a new Freshdesk contact.

        Use when registering a new customer contact. To update an existing contact, use update_contact instead.

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

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=True))
    async def update_contact(
        contact_id: Annotated[int, Field(description="The Freshdesk contact ID to update.")],
        name: Annotated[Optional[str], Field(description="Optional updated full name.")] = None,
        email: Annotated[Optional[str], Field(description="Optional updated email address.")] = None,
        phone: Annotated[Optional[str], Field(description="Optional updated phone number.")] = None,
        mobile: Annotated[Optional[str], Field(description="Optional updated mobile number.")] = None,
        company_id: Annotated[
            Optional[int], Field(description="Optional updated company ID association.")
        ] = None,
    ) -> dict:
        """Update an existing Freshdesk contact. Only provided fields are changed.

        Use when modifying existing contact information. To add a new contact, use create_contact instead.

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
            return cast(
                dict, client._handle_response(await c.put(f"/contacts/{contact_id}", json=payload))
            )

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=True, idempotentHint=True))
    async def delete_contact(
        contact_id: Annotated[int, Field(description="The Freshdesk contact ID to soft-delete.")]
    ) -> dict:
        """Delete (soft-delete) a Freshdesk contact by ID. Moves contact to deleted state.

        Use to remove obsolete contacts. To clear specific fields without deleting, use update_contact.

        Args:
            contact_id: The Freshdesk contact ID to delete.
        """
        async with client._client() as c:
            return cast(dict, client._handle_response(await c.delete(f"/contacts/{contact_id}")))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def search_contacts(
        query: Annotated[
            str, Field(description="Contact search query string (e.g. 'name:John' or 'email:john@example.com').")
        ]
    ) -> list[dict]:
        """Search contacts using Freshdesk search query syntax.

        Use when searching for contacts by partial name, domain, or custom field criteria.
        To browse all contacts sequentially, use list_contacts instead.

        Args:
            query: Freshdesk contact search query string.
        """
        async with client._client() as c:
            data = client._handle_response(
                await c.get(
                    "/search/contacts", params={"query": client._format_search_query(query)}
                )
            )
        results = data.get("results", data) if isinstance(data, dict) else data
        return cast(list[dict], results)

