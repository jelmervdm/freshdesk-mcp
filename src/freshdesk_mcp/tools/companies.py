from typing import Any, Optional, cast
from mcp.server.fastmcp import FastMCP

from freshdesk_mcp import client


def register(mcp: FastMCP) -> None:
    """Register company management tools."""

    @mcp.tool()
    async def list_companies(page: int = 1, per_page: int = 30) -> list[dict]:
        """List Freshdesk customer companies.

        Args:
            page: Page number (1-indexed).
            per_page: Results per page (max 100).
        """
        params = {"page": page, "per_page": min(per_page, 100)}
        async with client._client() as c:
            return cast(list[dict], client._handle_response(await c.get("/companies", params=params)))

    @mcp.tool()
    async def get_company(company_id: int) -> dict:
        """Get details of a single Freshdesk company by ID.

        Args:
            company_id: The Freshdesk company ID.
        """
        async with client._client() as c:
            return cast(dict, client._handle_response(await c.get(f"/companies/{company_id}")))

    @mcp.tool()
    async def create_company(
        name: str,
        description: Optional[str] = None,
        domains: Optional[list[str]] = None,
        note: Optional[str] = None,
    ) -> dict:
        """Create a new Freshdesk company.

        Args:
            name: Name of the company (required).
            description: Description of the company.
            domains: Optional list of domain names associated with the company (e.g. ["example.com"]).
            note: Internal notes about the company.
        """
        payload: dict[str, Any] = {"name": name}
        if description:
            payload["description"] = description
        if domains:
            payload["domains"] = domains
        if note:
            payload["note"] = note

        async with client._client() as c:
            return cast(dict, client._handle_response(await c.post("/companies", json=payload)))

    @mcp.tool()
    async def update_company(
        company_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        domains: Optional[list[str]] = None,
        note: Optional[str] = None,
    ) -> dict:
        """Update an existing Freshdesk company. Only provided fields are changed.

        Args:
            company_id: The Freshdesk company ID to update.
            name: Optional updated company name.
            description: Optional updated description.
            domains: Optional updated list of domains.
            note: Optional updated internal notes.
        """
        payload: dict[str, Any] = {}
        if name is not None:
            payload["name"] = name
        if description is not None:
            payload["description"] = description
        if domains is not None:
            payload["domains"] = domains
        if note is not None:
            payload["note"] = note

        if not payload:
            raise ValueError("No fields provided to update.")

        async with client._client() as c:
            return cast(dict, client._handle_response(await c.put(f"/companies/{company_id}", json=payload)))

    @mcp.tool()
    async def delete_company(company_id: int) -> dict:
        """Delete (soft-delete) a Freshdesk company by ID.

        Args:
            company_id: The Freshdesk company ID to delete.
        """
        async with client._client() as c:
            return cast(dict, client._handle_response(await c.delete(f"/companies/{company_id}")))

    @mcp.tool()
    async def search_companies(query: str) -> list[dict]:
        """Search companies using Freshdesk search query syntax (e.g. '"name:Acme"').

        Args:
            query: Freshdesk company search query string.
        """
        async with client._client() as c:
            data = client._handle_response(await c.get("/search/companies", params={"query": f'"{query}"'}))
        results = data.get("results", data) if isinstance(data, dict) else data
        return cast(list[dict], results)
