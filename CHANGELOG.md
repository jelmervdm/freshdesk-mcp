# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/) and this project adheres to [Semantic Versioning](https://semver.org/).

## [0.2.0] - 2026-07-26

### Added
- Companies domain tools (`list_companies`, `get_company`, `create_company`, `update_company`, `delete_company`, `search_companies`).
- Time tracking tools (`list_time_entries`, `create_time_entry`, `update_time_entry`, `delete_time_entry`).
- Solutions / Knowledge base tools (`list_solution_categories`, `list_solution_folders`, `list_solution_articles`, `get_solution_article`, `search_solution_articles`).
- Expanded Contact tools (`get_contact`, `update_contact`, `delete_contact`, `search_contacts`).
- Ticket field metadata (`get_ticket_fields`) and ticket restoration (`restore_ticket`).
- Dynamic MCP Resources (`freshdesk://ticket-fields`, `freshdesk://agents`).
- Workflow MCP Prompt templates (`triage_ticket`, `draft_reply`).

### Changed
- Migrated HTTP execution layer to non-blocking `httpx.AsyncClient`.
- Enhanced API error response formatting for structured validation error messages.

## [0.1.0] - 2026-07-25

### Added
- Initial release of Freshdesk MCP server package.
- Exposed ticket management tools (list, search, create, update, delete, reply, private note).
- Exposed contact management tools (list, search, create).
- Exposed agent and group listing tools.
- Integrated semantic tool routing (`TOOL_ROUTING`) via `fastembed` and `numpy`.
- Integrated ContextForge Gateway support (`ENABLE_CONTEXTFORGE_GATEWAY`) natively.
- Docker configuration (`Dockerfile`, `docker-compose.yml`, `entrypoint.sh`).
- GitHub Actions CI/CD workflows for publication, testing, linting, and security audits.
- Full test suite verifying tool registration, client mocking, and semantic routing.
