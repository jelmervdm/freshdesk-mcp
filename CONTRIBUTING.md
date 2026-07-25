# Contributing to freshdesk-mcp

Thanks for your interest in contributing! This document covers everything you need to get started.

## Getting Started

```bash
git clone https://github.com/jelmervdm/freshdesk-mcp.git
cd freshdesk-mcp

python3 -m venv venv
source venv/bin/activate

pip install -e .
pip install -r requirements-dev.txt
pip install pre-commit
pre-commit install
```

## Running Tests

```bash
pytest tests/ -v
```

## Code Quality

This project enforces linting, type checking, and formatting via pre-commit hooks. They run automatically on `git commit` once installed. You can also run them manually:

```bash
pre-commit run --all-files
```

Individual tools:

```bash
flake8 src/freshdesk_mcp/   # linting
mypy src/freshdesk_mcp/     # type checking
black src/freshdesk_mcp/    # formatting
```

## Submitting a Pull Request

1. Fork the repo and create a branch from `main`
2. Make your changes, including tests for any new behaviour
3. Ensure all checks pass (`pytest`, `flake8`, `mypy`, `black`)
4. Open a PR against `main`

## Commit Message Convention

This project uses [Conventional Commits](https://www.conventionalcommits.org/) and [python-semantic-release](https://python-semantic-release.readthedocs.io/) for automated versioning. **Your commit messages directly determine the next version number**, so please follow the format:

| Prefix | When to use | Version bump |
|--------|-------------|--------------|
| `fix:` | A bug fix | Patch (`0.1.0` → `0.1.1`) |
| `feat:` | A new feature | Minor (`0.1.0` → `0.2.0`) |
| `feat!:` or `BREAKING CHANGE:` in footer | A breaking API change | Major (`0.1.0` → `1.0.0`) |
| `chore:`, `docs:`, `test:`, `ci:`, `refactor:` | Everything else | No bump |

Examples:

```
feat: add support for listing ticket groups
fix: resolve 400 Bad Request error when updating responder ID
feat!: rename FRESHDESK_DOMAIN to FRESHDESK_URL
```

Commits that don't follow this format won't break anything, but they won't trigger a release either.

## Security

Please do not open public issues for security vulnerabilities. See [SECURITY.md](SECURITY.md) for the responsible disclosure process.
