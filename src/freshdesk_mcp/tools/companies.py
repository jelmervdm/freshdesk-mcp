from typing import Annotated, Any, Optional, cast
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from freshdesk_mcp import client


def register(mcp: FastMCP) -> None:
    """Register company management tools."""

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def list_companies(
        page: Annotated[int, Field(description="Page number (1-indexed).")] = 1,
        per_page: Annotated[int, Field(description="Results per page (max 100).")] = 30,
    ) -> list[dict]:
        """List Freshdesk customer companies sequentially.

        Use when browsing company accounts. To search companies by keyword or name, use search_companies.
        To fetch details for a single company ID, use get_company.

        Args:
            page: Page number (1-indexed).
            per_page: Results per page (max 100).
        """
        params = {"page": page, "per_page": min(per_page, 100)}
        async with client._client() as c:
            return cast(
                list[dict], client._handle_response(await c.get("/companies", params=params))
            )

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def get_company(
        company_id: Annotated[int, Field(description="The Freshdesk company ID.")]
    ) -> dict:
        """Get details of a single Freshdesk company by ID.

        Use when inspecting a known company account by ID. To browse all companies, use list_companies.

        Args:
            company_id: The Freshdesk company ID.
        """
        async with client._client() as c:
            return cast(dict, client._handle_response(await c.get(f"/companies/{company_id}")))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=False))
    async def create_company(
        name: Annotated[str, Field(description="Name of the company (required).")],
        description: Annotated[
            Optional[str], Field(description="Description of company profile.")
        ] = None,
        domains: Annotated[
            Optional[list[str]], Field(description="Associated domain names (e.g. ['example.com']).")
        ] = None,
        note: Annotated[Optional[str], Field(description="Internal notes about company.")] = None,
    ) -> dict:
        """Create a new Freshdesk company account.

        Use when registering a new company account. To update an existing company, use update_company instead.

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

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=True))
    async def update_company(
        company_id: Annotated[int, Field(description="The Freshdesk company ID to update.")],
        name: Annotated[Optional[str], Field(description="Optional updated company name.")] = None,
        description: Annotated[
            Optional[str], Field(description="Optional updated description.")
        ] = None,
        domains: Annotated[
            Optional[list[str]], Field(description="Optional updated list of domain names.")
        ] = None,
        note: Annotated[
            Optional[str], Field(description="Optional updated internal notes.")
        ] = None,
    ) -> dict:
        """Update an existing Freshdesk company. Only provided fields are changed.

        Use when modifying company details. To register a new company, use create_company.

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
            return cast(
                dict, client._handle_response(await c.put(f"/companies/{company_id}", json=payload))
            )

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=True, idempotentHint=True))
    async def delete_company(
        company_id: Annotated[int, Field(description="The Freshdesk company ID to soft-delete.")]
    ) -> dict:
        """Delete (soft-delete) a Freshdesk company by ID.

        Use to delete obsolete company records. To clear individual fields without deleting, use update_company.

        Args:
            company_id: The Freshdesk company ID to delete.
        """
        async with client._client() as c:
            return cast(dict, client._handle_response(await c.delete(f"/companies/{company_id}")))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def search_companies(
        query: Annotated[
            str, Field(description="Company search query string (e.g. 'name:Acme').")
        ]
    ) -> list[dict]:
        """Search companies using Freshdesk search query syntax.

        Use when querying companies by keyword or name filter. To browse all companies sequentially, use list_companies.

        Args:
            query: Freshdesk company search query string.
        """
        async with client._client() as c:
            data = client._handle_response(
                await c.get(
                    "/search/companies", params={"query": client._format_search_query(query)}
                )
            )
        results = data.get("results", data) if isinstance(data, dict) else data
        return cast(list[dict], results)

