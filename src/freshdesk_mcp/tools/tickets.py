from typing import Any, Optional, cast
from mcp.server.fastmcp import FastMCP

from freshdesk_mcp import client


def register(mcp: FastMCP) -> None:
    """Register ticket management tools."""

    @mcp.tool()
    async def list_tickets(
        page: int = 1,
        per_page: int = 30,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        order_by: str = "created_at",
        order_type: str = "desc",
    ) -> list[dict]:
        """List Freshdesk tickets, with optional filters.

        Args:
            page: Page number (1-indexed).
            per_page: Results per page (max 100).
            status: Optional filter: one of "open", "pending", "resolved", "closed".
            priority: Optional filter: one of "low", "medium", "high", "urgent".
            order_by: Field to sort by (e.g. "created_at", "updated_at", "priority").
            order_type: "asc" or "desc".
        """
        params: dict[str, Any] = {
            "page": page,
            "per_page": min(per_page, 100),
            "order_by": order_by,
            "order_type": order_type,
        }
        if status:
            if status not in client.STATUS_MAP:
                raise ValueError(f"Invalid status '{status}'. Use one of {list(client.STATUS_MAP)}")
            params["status"] = client.STATUS_MAP[status]
        if priority:
            if priority not in client.PRIORITY_MAP:
                raise ValueError(f"Invalid priority '{priority}'. Use one of {list(client.PRIORITY_MAP)}")
            params["priority"] = client.PRIORITY_MAP[priority]

        async with client._client() as c:
            data = client._handle_response(await c.get("/tickets", params=params))
        return [client._simplify_ticket(t) for t in data]

    @mcp.tool()
    async def get_ticket(ticket_id: int, include_conversations: bool = False) -> dict:
        """Get full details of a single ticket by ID.

        Args:
            ticket_id: The Freshdesk ticket ID.
            include_conversations: If true, also fetch and include the ticket's
                conversation thread (replies and notes).
        """
        async with client._client() as c:
            ticket = cast(dict, client._handle_response(await c.get(f"/tickets/{ticket_id}")))
            if include_conversations:
                convos = cast(list, client._handle_response(await c.get(f"/tickets/{ticket_id}/conversations")))
                ticket["conversations"] = convos
        return ticket

    @mcp.tool()
    async def search_tickets(query: str) -> list[dict]:
        """Search tickets using Freshdesk's query syntax.

        Args:
            query: A Freshdesk search query, e.g.
                '"priority:3 AND status:2"' or '"subject:'billing issue'"'.
                See https://developers.freshdesk.com/api/#filter_tickets for syntax.
                Do not include surrounding quotes beyond what the syntax needs;
                this tool will wrap the query for you.
        """
        async with client._client() as c:
            data = client._handle_response(await c.get("/search/tickets", params={"query": f'"{query}"'}))
        results = data.get("results", data) if isinstance(data, dict) else data
        return [client._simplify_ticket(t) for t in results]

    @mcp.tool()
    async def create_ticket(
        subject: str,
        description: str,
        email: str,
        priority: str = "medium",
        status: str = "open",
        source: str = "portal",
        tags: Optional[list[str]] = None,
        group_id: Optional[int] = None,
        responder_id: Optional[int] = None,
    ) -> dict:
        """Create a new Freshdesk ticket.

        Args:
            subject: Ticket subject line.
            description: Ticket body/description (HTML or plain text).
            email: Email address of the requester (customer).
            priority: One of "low", "medium", "high", "urgent".
            status: One of "open", "pending", "resolved", "closed".
            source: One of "email", "portal", "phone", "chat", "feedback_widget",
                "outbound_email".
            tags: Optional list of tag strings.
            group_id: Optional Freshdesk group ID to assign the ticket to.
            responder_id: Optional agent ID to assign the ticket to.
        """
        if priority not in client.PRIORITY_MAP:
            raise ValueError(f"Invalid priority '{priority}'. Use one of {list(client.PRIORITY_MAP)}")
        if status not in client.STATUS_MAP:
            raise ValueError(f"Invalid status '{status}'. Use one of {list(client.STATUS_MAP)}")
        if source not in client.SOURCE_MAP:
            raise ValueError(f"Invalid source '{source}'. Use one of {list(client.SOURCE_MAP)}")

        payload: dict[str, Any] = {
            "subject": subject,
            "description": description,
            "email": email,
            "priority": client.PRIORITY_MAP[priority],
            "status": client.STATUS_MAP[status],
            "source": client.SOURCE_MAP[source],
        }
        if tags:
            payload["tags"] = tags
        if group_id is not None:
            payload["group_id"] = group_id
        if responder_id is not None:
            payload["responder_id"] = responder_id

        async with client._client() as c:
            return cast(dict, client._handle_response(await c.post("/tickets", json=payload)))

    @mcp.tool()
    async def update_ticket(
        ticket_id: int,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        subject: Optional[str] = None,
        tags: Optional[list[str]] = None,
        responder_id: Optional[int] = None,
        group_id: Optional[int] = None,
    ) -> dict:
        """Update fields on an existing ticket. Only provided fields are changed.

        Args:
            ticket_id: The Freshdesk ticket ID to update.
            status: Optional new status: "open", "pending", "resolved", "closed".
            priority: Optional new priority: "low", "medium", "high", "urgent".
            subject: Optional new subject line.
            tags: Optional new list of tags (replaces existing tags).
            responder_id: Optional agent ID to (re)assign the ticket to.
            group_id: Optional group ID to (re)assign the ticket to.
        """
        payload: dict[str, Any] = {}
        if status is not None:
            if status not in client.STATUS_MAP:
                raise ValueError(f"Invalid status '{status}'. Use one of {list(client.STATUS_MAP)}")
            payload["status"] = client.STATUS_MAP[status]
        if priority is not None:
            if priority not in client.PRIORITY_MAP:
                raise ValueError(f"Invalid priority '{priority}'. Use one of {list(client.PRIORITY_MAP)}")
            payload["priority"] = client.PRIORITY_MAP[priority]
        if subject is not None:
            payload["subject"] = subject
        if tags is not None:
            payload["tags"] = tags
        if responder_id is not None:
            payload["responder_id"] = responder_id
        if group_id is not None:
            payload["group_id"] = group_id

        if not payload:
            raise ValueError("No fields provided to update.")

        async with client._client() as c:
            return cast(dict, client._handle_response(await c.put(f"/tickets/{ticket_id}", json=payload)))

    @mcp.tool()
    async def delete_ticket(ticket_id: int) -> dict:
        """Delete (soft-delete) a ticket by ID. Freshdesk moves it to the trash."""
        async with client._client() as c:
            return cast(dict, client._handle_response(await c.delete(f"/tickets/{ticket_id}")))

    @mcp.tool()
    async def restore_ticket(ticket_id: int) -> dict:
        """Restore a soft-deleted ticket from the trash.

        Args:
            ticket_id: The Freshdesk ticket ID to restore.
        """
        async with client._client() as c:
            return cast(dict, client._handle_response(await c.put(f"/tickets/{ticket_id}/restore")))

    @mcp.tool()
    async def add_reply(ticket_id: int, body: str) -> dict:
        """Add a public reply to a ticket (visible to the customer).

        Args:
            ticket_id: The Freshdesk ticket ID.
            body: The reply content (HTML or plain text).
        """
        async with client._client() as c:
            return cast(dict, client._handle_response(await c.post(f"/tickets/{ticket_id}/reply", json={"body": body})))

    @mcp.tool()
    async def add_private_note(ticket_id: int, body: str, notify_agent_ids: Optional[list[int]] = None) -> dict:
        """Add a private/internal note to a ticket (not visible to the customer).

        Args:
            ticket_id: The Freshdesk ticket ID.
            body: The note content (HTML or plain text).
            notify_agent_ids: Optional list of agent IDs to notify about the note.
        """
        payload: dict[str, Any] = {"body": body, "private": True}
        if notify_agent_ids:
            payload["notify_emails"] = notify_agent_ids
        async with client._client() as c:
            return cast(dict, client._handle_response(await c.post(f"/tickets/{ticket_id}/notes", json=payload)))

    @mcp.tool()
    async def get_ticket_fields() -> list[dict]:
        """Fetch ticket form fields metadata including custom fields and dropdown choices."""
        async with client._client() as c:
            return cast(list[dict], client._handle_response(await c.get("/ticket_fields")))
