from mcp.server.fastmcp import FastMCP


def register(mcp: FastMCP) -> None:
    """Register MCP prompt templates."""

    @mcp.prompt()
    def triage_ticket(ticket_id: int, context: str = "") -> str:
        """Prompt template for triaging, categorizing, and assigning a ticket."""
        return f"""You are a Freshdesk support triaging assistant.
Analyze ticket #{ticket_id}.
Additional Context: {context if context else 'None provided'}

Follow these steps:
1. Call `get_ticket(ticket_id={ticket_id}, include_conversations=True)` to inspect the full ticket thread.
2. Call `get_ticket_fields()` to inspect valid priorities, statuses, and field definitions.
3. Recommend:
   - Appropriate priority (low, medium, high, urgent)
   - Assignment (group_id / responder_id)
   - Actionable next steps or drafted response
"""

    @mcp.prompt()
    def draft_reply(ticket_id: int, tone: str = "professional") -> str:
        """Prompt template to draft a customer reply for a ticket."""
        return f"""You are drafting a customer support response for Freshdesk ticket #{ticket_id}.
Desired Tone: {tone}

Instructions:
1. Call `get_ticket(ticket_id={ticket_id}, include_conversations=True)` to review customer messages.
2. Search knowledge base articles using `search_solution_articles` if applicable.
3. Draft a clear, helpful response.
4. Present the response for review before invoking `add_reply`.
"""
