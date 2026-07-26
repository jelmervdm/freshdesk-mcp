from typing import cast
from mcp.server.fastmcp import FastMCP

from freshdesk_mcp import client


def register(mcp: FastMCP) -> None:
    """Register solution / knowledge base tools."""

    @mcp.tool()
    async def list_solution_categories() -> list[dict]:
        """List knowledge base solution categories."""
        async with client._client() as c:
            return cast(list[dict], client._handle_response(await c.get("/solutions/categories")))

    @mcp.tool()
    async def list_solution_folders(category_id: int) -> list[dict]:
        """List solution folders within a specific category.

        Args:
            category_id: The category ID.
        """
        async with client._client() as c:
            return cast(
                list[dict],
                client._handle_response(
                    await c.get(f"/solutions/categories/{category_id}/folders")
                ),
            )

    @mcp.tool()
    async def list_solution_articles(folder_id: int) -> list[dict]:
        """List solution articles within a specific folder.

        Args:
            folder_id: The folder ID.
        """
        async with client._client() as c:
            return cast(
                list[dict],
                client._handle_response(await c.get(f"/solutions/folders/{folder_id}/articles")),
            )

    @mcp.tool()
    async def get_solution_article(article_id: int) -> dict:
        """Get full details of a solution knowledge base article by ID.

        Args:
            article_id: The solution article ID.
        """
        async with client._client() as c:
            return cast(
                dict, client._handle_response(await c.get(f"/solutions/articles/{article_id}"))
            )

    @mcp.tool()
    async def search_solution_articles(query: str) -> list[dict]:
        """Search solution knowledge base articles using a keyword query.

        Args:
            query: The search term or keywords to query.
        """
        async with client._client() as c:
            data = client._handle_response(await c.get("/search/solutions", params={"term": query}))
        results = data.get("results", data) if isinstance(data, dict) else data
        return cast(list[dict], results)
