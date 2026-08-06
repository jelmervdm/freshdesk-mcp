# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/) and this project adheres to [Semantic Versioning](https://semver.org/).

## [0.3.2] - 2026-08-06

### Fixed
- **Ticket Search API Documentation**: Updated `search_tickets` docstring to explicitly list supported search fields (`agent_id`, `group_id`, `priority`, `status`, `type`, `created_at`, `updated_at`, `due_by`, `company_id`, `tag`) and clarify that `subject`, `description`, and free-text queries are unsupported by Freshdesk's `/api/v2/search/tickets` endpoint (advising client-side filtering via `list_tickets` instead).
- Updated unit test `test_search_tickets` to query with supported field `tag:billing` instead of `subject:billing`.

## [0.3.0] - 2026-07-28

### Added
- Raw REST API v2 access tool (`raw_api_request`) supporting arbitrary HTTP requests (`GET`, `POST`, `PUT`, `DELETE`, `PATCH`), endpoint path normalization, query parameter forwarding, JSON payload handling, and TDQS compliance (`destructiveHint=True`).

## [0.2.3] - 2026-07-27

### Changed
- **Tool Definition Quality Score (TDQS) Optimization**: Upgraded all 35 FastMCP tool definitions to Tier A+ status (score 4.7 / 5.0).
- Added explicit FastMCP `ToolAnnotations` (`readOnlyHint`, `destructiveHint`, `idempotentHint`) across all tool decorators for client safety and UI hint rendering.
- Converted parameter type annotations to `Annotated[T, Field(description=...)]` for 100% parameter coverage in exposed JSON schemas.
- Expanded tool docstrings with explicit operational usage guidelines and named alternative tool guidance.

## [0.2.2] - 2026-07-26

### Fixed
- Redirected container entrypoint `echo` startup messages to `stderr` (`>&2`). Prevents non-JSON-RPC output on `stdout` which caused stdio MCP clients (such as Antigravity) to fail initialization with `invalid character 'S' looking for beginning of value`.

## [0.2.1] - 2026-07-26

### Added
- Automatic domain sanitization for `FRESHDESK_DOMAIN` environment variable.
- Utility `_format_search_query()` to strip redundant outer quotes before query execution.
- Comprehensive test coverage for search formatting, domain sanitization, tool routing, and missing tool functions.

### Changed
- Refactored `client._client()` to manage persistent `httpx.AsyncClient` connection pools.
- Updated `call_routed_tool` to allow safe lookup of any registered tool in routed mode.
- Updated Dockerfile base image to `python:3.12-slim`.

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
