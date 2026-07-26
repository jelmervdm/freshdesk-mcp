import json
from mcp.server.fastmcp import FastMCP
from freshdesk_mcp import client


def register(mcp: FastMCP) -> None:
    """Register MCP resources."""

    @mcp.resource("freshdesk://ticket-fields")
    async def get_ticket_fields_resource() -> str:
        """Resource providing ticket form definitions and custom field schemas."""
        async with client._client() as c:
            fields = client._handle_response(await c.get("/ticket_fields"))
        return json.dumps(fields, indent=2)

    @mcp.resource("freshdesk://agents")
    async def get_agents_resource() -> str:
        """Resource providing active support staff agents."""
        async with client._client() as c:
            agents = client._handle_response(await c.get("/agents"))
        return json.dumps(agents, indent=2)
