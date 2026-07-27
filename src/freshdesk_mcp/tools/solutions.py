from typing import Annotated, cast
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from freshdesk_mcp import client


def register(mcp: FastMCP) -> None:
    """Register solution / knowledge base tools."""

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def list_solution_categories() -> list[dict]:
        """List knowledge base solution categories.

        Use to browse top-level solution hierarchy. To list folders within a category, use list_solution_folders.
        """
        async with client._client() as c:
            return cast(list[dict], client._handle_response(await c.get("/solutions/categories")))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def list_solution_folders(
        category_id: Annotated[int, Field(description="The category ID.")]
    ) -> list[dict]:
        """List solution folders within a specific category.

        Use to navigate folders in a category. To list articles in a folder, use list_solution_articles.

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

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def list_solution_articles(
        folder_id: Annotated[int, Field(description="The folder ID.")]
    ) -> list[dict]:
        """List solution articles within a specific folder.

        Use to list articles in a knowledge base folder. To get the content of a specific article, use get_solution_article.

        Args:
            folder_id: The folder ID.
        """
        async with client._client() as c:
            return cast(
                list[dict],
                client._handle_response(await c.get(f"/solutions/folders/{folder_id}/articles")),
            )

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def get_solution_article(
        article_id: Annotated[int, Field(description="The solution article ID.")]
    ) -> dict:
        """Get full details of a solution knowledge base article by ID.

        Use to read the full body content of an article. To search across articles, use search_solution_articles.

        Args:
            article_id: The solution article ID.
        """
        async with client._client() as c:
            return cast(
                dict, client._handle_response(await c.get(f"/solutions/articles/{article_id}"))
            )

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def search_solution_articles(
        query: Annotated[str, Field(description="The search term or keywords to query.")]
    ) -> list[dict]:
        """Search solution knowledge base articles using a keyword query.

        Use when looking for help articles matching specific keywords. To browse category structure, use list_solution_categories.

        Args:
            query: The search term or keywords to query.
        """
        async with client._client() as c:
            data = client._handle_response(await c.get("/search/solutions", params={"term": query}))
        results = data.get("results", data) if isinstance(data, dict) else data
        return cast(list[dict], results)

