from typing import Any, Optional, cast
from mcp.server.fastmcp import FastMCP

from freshdesk_mcp import client


def register(mcp: FastMCP) -> None:
    """Register time tracking tools."""

    @mcp.tool()
    async def list_time_entries(ticket_id: int) -> list[dict]:
        """List time entries logged on a specific Freshdesk ticket.

        Args:
            ticket_id: The Freshdesk ticket ID.
        """
        async with client._client() as c:
            return cast(
                list[dict],
                client._handle_response(await c.get(f"/tickets/{ticket_id}/time_entries")),
            )

    @mcp.tool()
    async def create_time_entry(
        ticket_id: int,
        time_spent: str,
        note: Optional[str] = None,
        billable: Optional[bool] = None,
        agent_id: Optional[int] = None,
    ) -> dict:
        """Log a new time entry on a ticket.

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

    @mcp.tool()
    async def update_time_entry(
        time_entry_id: int,
        time_spent: Optional[str] = None,
        note: Optional[str] = None,
        billable: Optional[bool] = None,
    ) -> dict:
        """Update an existing time entry. Only provided fields are updated.

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

    @mcp.tool()
    async def delete_time_entry(time_entry_id: int) -> dict:
        """Delete a time entry by ID.

        Args:
            time_entry_id: The time entry ID to delete.
        """
        async with client._client() as c:
            return cast(
                dict, client._handle_response(await c.delete(f"/time_entries/{time_entry_id}"))
            )
