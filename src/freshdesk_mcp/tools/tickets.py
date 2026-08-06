from typing import Annotated, Any, Optional, cast
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from freshdesk_mcp import client


def register(mcp: FastMCP) -> None:
    """Register ticket management tools."""

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def list_tickets(
        page: Annotated[int, Field(description="Page number (1-indexed).")] = 1,
        per_page: Annotated[int, Field(description="Results per page (max 100).")] = 30,
        status: Annotated[
            Optional[str],
            Field(description="Filter by status: 'open', 'pending', 'resolved', or 'closed'."),
        ] = None,
        priority: Annotated[
            Optional[str],
            Field(description="Filter by priority: 'low', 'medium', 'high', or 'urgent'."),
        ] = None,
        order_by: Annotated[
            str,
            Field(description="Field to sort by (e.g. 'created_at', 'updated_at', 'priority')."),
        ] = "created_at",
        order_type: Annotated[str, Field(description="Sort order: 'asc' or 'desc'.")] = "desc",
    ) -> list[dict]:
        """List Freshdesk tickets sequentially with optional filters.

        Use when browsing or listing tickets. To search by specific criteria or keywords,
        use search_tickets instead. To inspect full details of a specific ticket, use get_ticket.

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
                raise ValueError(
                    f"Invalid priority '{priority}'. Use one of {list(client.PRIORITY_MAP)}"
                )
            params["priority"] = client.PRIORITY_MAP[priority]

        async with client._client() as c:
            data = client._handle_response(await c.get("/tickets", params=params))
        return [client._simplify_ticket(t) for t in data]

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def get_ticket(
        ticket_id: Annotated[int, Field(description="The Freshdesk ticket ID.")],
        include_conversations: Annotated[
            bool, Field(description="If true, include ticket conversation thread.")
        ] = False,
    ) -> dict:
        """Get full details of a single ticket by ID.

        Use when inspecting a specific ticket by ID. To browse multiple tickets,
        use list_tickets or search_tickets instead.

        Args:
            ticket_id: The Freshdesk ticket ID.
            include_conversations: If true, also fetch and include the ticket's
                conversation thread (replies and notes).
        """
        async with client._client() as c:
            ticket = cast(dict, client._handle_response(await c.get(f"/tickets/{ticket_id}")))
            if include_conversations:
                convos = cast(
                    list,
                    client._handle_response(await c.get(f"/tickets/{ticket_id}/conversations")),
                )
                ticket["conversations"] = convos
        return ticket

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def search_tickets(
        query: Annotated[
            str,
            Field(description="Freshdesk search query string (e.g. 'priority:3 AND status:2')."),
        ],
    ) -> list[dict]:
        """Search tickets using Freshdesk's query syntax.

        Use when querying tickets by specific conditional rules (e.g. priority, status, type, tag).
        Note: Freshdesk search API ONLY supports filtering by specific fields: agent_id, group_id,
        priority, status, type, created_at, updated_at, due_by, company_id, and tag.
        Searching by 'subject', 'description', or free-text is NOT supported by Freshdesk's search API
        (use list_tickets to browse tickets and filter by subject client-side instead).

        Args:
            query: A Freshdesk search query, e.g.
                '"priority:3 AND status:2"' or '"type:\'Incident\' AND tag:\'billing\'"'.
                See https://developers.freshdesk.com/api/#filter_tickets for syntax.
                Do not include surrounding quotes beyond what the syntax needs;
                this tool will wrap the query for you.
        """
        async with client._client() as c:
            data = client._handle_response(
                await c.get("/search/tickets", params={"query": client._format_search_query(query)})
            )
        results = data.get("results", data) if isinstance(data, dict) else data
        return [client._simplify_ticket(t) for t in results]

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=False))
    async def create_ticket(
        subject: Annotated[str, Field(description="Ticket subject line.")],
        description: Annotated[
            str, Field(description="Ticket body/description (HTML or plain text).")
        ],
        email: Annotated[str, Field(description="Email address of the requester (customer).")],
        priority: Annotated[
            str, Field(description="Priority: 'low', 'medium', 'high', or 'urgent'.")
        ] = "medium",
        status: Annotated[
            str, Field(description="Status: 'open', 'pending', 'resolved', or 'closed'.")
        ] = "open",
        source: Annotated[
            str,
            Field(
                description="Source: 'email', 'portal', 'phone', 'chat', 'feedback_widget', or 'outbound_email'."
            ),
        ] = "portal",
        tags: Annotated[
            Optional[list[str]], Field(description="Optional list of tag strings.")
        ] = None,
        group_id: Annotated[
            Optional[int], Field(description="Optional group ID to assign the ticket to.")
        ] = None,
        responder_id: Annotated[
            Optional[int], Field(description="Optional agent ID to assign the ticket to.")
        ] = None,
    ) -> dict:
        """Create a new Freshdesk ticket.

        Use when creating new support tickets. To update an existing ticket, use update_ticket instead.

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
            raise ValueError(
                f"Invalid priority '{priority}'. Use one of {list(client.PRIORITY_MAP)}"
            )
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

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=True))
    async def update_ticket(
        ticket_id: Annotated[int, Field(description="The Freshdesk ticket ID to update.")],
        status: Annotated[
            Optional[str],
            Field(description="Optional new status: 'open', 'pending', 'resolved', 'closed'."),
        ] = None,
        priority: Annotated[
            Optional[str],
            Field(description="Optional new priority: 'low', 'medium', 'high', 'urgent'."),
        ] = None,
        subject: Annotated[Optional[str], Field(description="Optional new subject line.")] = None,
        tags: Annotated[
            Optional[list[str]], Field(description="Optional new list of tags (replaces existing).")
        ] = None,
        responder_id: Annotated[
            Optional[int], Field(description="Optional agent ID to (re)assign ticket to.")
        ] = None,
        group_id: Annotated[
            Optional[int], Field(description="Optional group ID to (re)assign ticket to.")
        ] = None,
    ) -> dict:
        """Update fields on an existing ticket. Only provided fields are changed.

        Use when updating fields of an existing ticket. To create a new ticket, use create_ticket.

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
                raise ValueError(
                    f"Invalid priority '{priority}'. Use one of {list(client.PRIORITY_MAP)}"
                )
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
            return cast(
                dict, client._handle_response(await c.put(f"/tickets/{ticket_id}", json=payload))
            )

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=True, idempotentHint=True))
    async def delete_ticket(
        ticket_id: Annotated[int, Field(description="The Freshdesk ticket ID to soft-delete.")],
    ) -> dict:
        """Delete (soft-delete) a ticket by ID. Freshdesk moves it to the trash.

        Operation is reversible via restore_ticket. To close a ticket without deleting, use update_ticket(status='closed').

        Args:
            ticket_id: The Freshdesk ticket ID to delete.
        """
        async with client._client() as c:
            return cast(dict, client._handle_response(await c.delete(f"/tickets/{ticket_id}")))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=True))
    async def restore_ticket(
        ticket_id: Annotated[int, Field(description="The Freshdesk ticket ID to restore.")],
    ) -> dict:
        """Restore a soft-deleted ticket from the trash.

        Use to recover soft-deleted tickets from trash. To browse active tickets, use list_tickets.

        Args:
            ticket_id: The Freshdesk ticket ID to restore.
        """
        async with client._client() as c:
            return cast(dict, client._handle_response(await c.put(f"/tickets/{ticket_id}/restore")))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=False))
    async def add_reply(
        ticket_id: Annotated[int, Field(description="The Freshdesk ticket ID.")],
        body: Annotated[str, Field(description="Reply body content (HTML or plain text).")],
    ) -> dict:
        """Add a public reply to a ticket (visible to the customer).

        Use when communicating updates directly to the customer. For internal team notes, use add_private_note instead.

        Args:
            ticket_id: The Freshdesk ticket ID.
            body: The reply content (HTML or plain text).
        """
        async with client._client() as c:
            return cast(
                dict,
                client._handle_response(
                    await c.post(f"/tickets/{ticket_id}/reply", json={"body": body})
                ),
            )

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=False))
    async def add_private_note(
        ticket_id: Annotated[int, Field(description="The Freshdesk ticket ID.")],
        body: Annotated[str, Field(description="Note body content (HTML or plain text).")],
        notify_agent_ids: Annotated[
            Optional[list[int]], Field(description="Optional list of agent IDs to notify.")
        ] = None,
    ) -> dict:
        """Add a private/internal note to a ticket (not visible to the customer).

        Use for internal agent collaboration and internal documentation. For customer-visible replies, use add_reply.

        Args:
            ticket_id: The Freshdesk ticket ID.
            body: The note content (HTML or plain text).
            notify_agent_ids: Optional list of agent IDs to notify about the note.
        """
        payload: dict[str, Any] = {"body": body, "private": True}
        if notify_agent_ids:
            payload["notify_emails"] = notify_agent_ids
        async with client._client() as c:
            return cast(
                dict,
                client._handle_response(await c.post(f"/tickets/{ticket_id}/notes", json=payload)),
            )

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def get_ticket_fields() -> list[dict]:
        """Fetch ticket form fields metadata including custom fields and dropdown choices.

        Use to inspect field options and valid dropdown values before creating or updating tickets.
        """
        async with client._client() as c:
            return cast(list[dict], client._handle_response(await c.get("/ticket_fields")))
