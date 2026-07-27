from typing import Annotated, cast
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from freshdesk_mcp import client


def register(mcp: FastMCP) -> None:
    """Register agent and group listing tools."""

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def list_agents(
        page: Annotated[int, Field(description="Page number (1-indexed).")] = 1,
        per_page: Annotated[int, Field(description="Results per page (max 100).")] = 30,
    ) -> list[dict]:
        """List Freshdesk agents (support staff).

        Use to inspect available support agent staff IDs when assigning tickets or notes.

        Args:
            page: Page number (1-indexed).
            per_page: Results per page (max 100).
        """
        params = {"page": page, "per_page": min(per_page, 100)}
        async with client._client() as c:
            return cast(list[dict], client._handle_response(await c.get("/agents", params=params)))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def list_groups() -> list[dict]:
        """List Freshdesk groups (teams tickets can be assigned to).

        Use to inspect valid group team IDs before creating or re-assigning tickets.
        """
        async with client._client() as c:
            return cast(list[dict], client._handle_response(await c.get("/groups")))
