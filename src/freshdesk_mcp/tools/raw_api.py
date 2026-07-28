from typing import Annotated, Any, Optional
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from freshdesk_mcp import client

VALID_METHODS = {"GET", "POST", "PUT", "DELETE", "PATCH"}


def register(mcp: FastMCP) -> None:
    """Register raw API access tools."""

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=True, readOnlyHint=False, idempotentHint=False))
    async def raw_api_request(
        method: Annotated[
            str,
            Field(description="HTTP method: 'GET', 'POST', 'PUT', 'DELETE', or 'PATCH'."),
        ],
        endpoint: Annotated[
            str,
            Field(description="API endpoint path relative to /api/v2 (e.g. '/tickets/123', 'contacts')."),
        ],
        params: Annotated[
            Optional[dict[str, Any]],
            Field(description="Optional query parameters key-value dictionary."),
        ] = None,
        data: Annotated[
            Optional[Any],
            Field(description="Optional request JSON body (object, array, string, number, or boolean)."),
        ] = None,
    ) -> Any:
        """Execute a raw HTTP request directly against the Freshdesk REST API v2.

        Use when executing custom operations, advanced queries, or interacting with endpoints
        (such as custom objects, ticket fields, or admin APIs) not covered by specialized MCP tools.

        Args:
            method: HTTP method ('GET', 'POST', 'PUT', 'DELETE', or 'PATCH').
            endpoint: Path relative to Freshdesk REST API v2 base URL.
            params: Optional dictionary of query parameters.
            data: Optional request payload sent as JSON body.
        """
        normalized_method = method.strip().upper()
        if normalized_method not in VALID_METHODS:
            raise ValueError(
                f"Invalid HTTP method '{method}'. Allowed methods: {sorted(VALID_METHODS)}"
            )

        path = endpoint.strip()
        if path.startswith("/api/v2"):
            path = path[len("/api/v2") :]
        elif path.startswith("api/v2"):
            path = path[len("api/v2") :]

        if not path.startswith("/"):
            path = f"/{path}"

        async with client._client() as c:
            resp = await c.request(
                method=normalized_method,
                url=path,
                params=params,
                json=data,
            )
            return client._handle_response(resp)
