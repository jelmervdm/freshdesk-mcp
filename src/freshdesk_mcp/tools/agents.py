from typing import cast
from mcp.server.fastmcp import FastMCP

from freshdesk_mcp import client


def register(mcp: FastMCP) -> None:
    """Register agent and group listing tools."""

    @mcp.tool()
    def list_agents(page: int = 1, per_page: int = 30) -> list[dict]:
        """List Freshdesk agents (support staff)."""
        params = {"page": page, "per_page": min(per_page, 100)}
        with client._client() as c:
            return cast(list[dict], client._handle_response(c.get("/agents", params=params)))

    @mcp.tool()
    def list_groups() -> list[dict]:
        """List Freshdesk groups (teams tickets can be assigned to)."""
        with client._client() as c:
            return cast(list[dict], client._handle_response(c.get("/groups")))
