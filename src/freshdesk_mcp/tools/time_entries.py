from typing import Annotated, Any, Optional, cast
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from freshdesk_mcp import client


def register(mcp: FastMCP) -> None:
    """Register time tracking tools."""

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def list_time_entries(
        ticket_id: Annotated[int, Field(description="The Freshdesk ticket ID.")]
    ) -> list[dict]:
        """List time entries logged on a specific Freshdesk ticket.

        Use when inspecting time tracking history for a ticket. To log new time, use create_time_entry.

        Args:
            ticket_id: The Freshdesk ticket ID.
        """
        async with client._client() as c:
            return cast(
                list[dict],
                client._handle_response(await c.get(f"/tickets/{ticket_id}/time_entries")),
            )

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=False))
    async def create_time_entry(
        ticket_id: Annotated[int, Field(description="The Freshdesk ticket ID.")],
        time_spent: Annotated[
            str, Field(description="Time spent formatted as 'hh:mm' or 'mm' (e.g. '01:30' or '45').")
        ],
        note: Annotated[Optional[str], Field(description="Optional description/note of work done.")] = None,
        billable: Annotated[
            Optional[bool], Field(description="Optional boolean indicating whether time is billable.")
        ] = None,
        agent_id: Annotated[
            Optional[int], Field(description="Optional agent ID who performed the work.")
        ] = None,
    ) -> dict:
        """Log a new time entry on a ticket.

        Use when recording time spent on customer support work. To update existing logged time, use update_time_entry instead.

        Args:
            ticket_id: The Freshdesk ticket ID.
            time_spent: Time spent formatted as "hh:mm" or "mm" (e.g. "01:30" or "45").
            note: Optional description/note of work done.
            billable: Optional boolean indicating whether the time is billable.
            agent_id: Optional Freshdesk agent ID who performed the work.
        """
        payload: dict[str, Any] = {"time_spent": time_spent}
        if note:
            payload["note"] = note
        if billable is not None:
            payload["billable"] = billable
        if agent_id is not None:
            payload["agent_id"] = agent_id

        async with client._client() as c:
            return cast(
                dict,
                client._handle_response(
                    await c.post(f"/tickets/{ticket_id}/time_entries", json=payload)
                ),
            )

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=True))
    async def update_time_entry(
        time_entry_id: Annotated[int, Field(description="The time entry ID.")],
        time_spent: Annotated[
            Optional[str], Field(description="Optional updated time spent (e.g. '02:00').")
        ] = None,
        note: Annotated[Optional[str], Field(description="Optional updated note.")] = None,
        billable: Annotated[
            Optional[bool], Field(description="Optional updated billable flag.")
        ] = None,
    ) -> dict:
        """Update an existing time entry. Only provided fields are updated.

        Use when adjusting logged time or notes. To log new work, use create_time_entry instead.

        Args:
            time_entry_id: The time entry ID.
            time_spent: Optional updated time spent (e.g. "02:00").
            note: Optional updated note.
            billable: Optional updated billable flag.
        """
        payload: dict[str, Any] = {}
        if time_spent is not None:
            payload["time_spent"] = time_spent
        if note is not None:
            payload["note"] = note
        if billable is not None:
            payload["billable"] = billable

        if not payload:
            raise ValueError("No fields provided to update.")

        async with client._client() as c:
            return cast(
                dict,
                client._handle_response(
                    await c.put(f"/time_entries/{time_entry_id}", json=payload)
                ),
            )

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=True, idempotentHint=True))
    async def delete_time_entry(
        time_entry_id: Annotated[int, Field(description="The time entry ID to delete.")]
    ) -> dict:
        """Delete a time entry by ID.

        Use to remove incorrectly logged time entries. To adjust logged duration, use update_time_entry instead.

        Args:
            time_entry_id: The time entry ID to delete.
        """
        async with client._client() as c:
            return cast(
                dict, client._handle_response(await c.delete(f"/time_entries/{time_entry_id}"))
            )

