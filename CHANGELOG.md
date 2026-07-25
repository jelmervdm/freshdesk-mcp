# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/) and this project adheres to [Semantic Versioning](https://semver.org/).

## [1.0.0] - 2026-07-25

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
