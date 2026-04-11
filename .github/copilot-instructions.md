# Platelet-Movie Development Guidelines

## Test-Driven Development (TDD)

**Always write the failing test before implementation.**

```python
# Workflow:
# 1. Write a failing test that defines desired behavior
# 2. Run test to confirm it fails
# 3. Write minimal code to make the test pass
# 4. Run test to confirm it passes
# 5. Refactor if needed while keeping tests green
```

- Every new feature or bug fix starts with a test
- Tests live in `tests/` and mirror the `platelet_movie/` structure
- Use `pytest` fixtures and mocking (`pytest-mock`) to isolate units
- Maintain **80% code coverage** minimum (enforced by `poe test`)

**Before creating or modifying any code:**
1. Identify what behavior needs to change
2. Write a test that would pass if the behavior existed
3. Run `poe test` to confirm the test fails
4. Only then implement the feature

## README Maintenance

**Update `README.md` in the same PR as code changes.**

When you add, modify, or remove:
- Features or CLI flags → Update "Features" and "Usage" sections
- Environment variables → Update "Configuration" table
- Installation steps or dependencies → Update "Installation" or "Requirements"
- Commands or workflows → Update examples and command documentation

The README is the primary user-facing documentation. Keep it current with every change.

## 12-Factor App Best Practices

This project follows [12-Factor App](https://12factor.net/) methodology:

### Config (Factor III)
- **All configuration via environment variables** (see `platelet_movie/config.py`)
- Never hardcode credentials, URLs, or tuning parameters
- Use `Config` dataclass for all settings with sensible defaults
- Document every new environment variable in README

### Dependencies (Factor II)
- Declare dependencies explicitly in `pyproject.toml`
- Use `poetry install` for reproducible builds
- Never rely on system-wide packages

### Dev/Prod Parity (Factor X)
- Same dependencies and configuration model in all environments
- Use feature flags (env vars) instead of code branches for behavior changes

## Secrets Management with Doppler

**Use [Doppler CLI](https://docs.doppler.com/docs/install-cli) for local development secrets.**

### Setup (one-time)
```bash
# Install Doppler CLI
brew install dopplerhq/cli/doppler  # macOS
# or visit https://docs.doppler.com/docs/install-cli

# Login and setup project
doppler login
doppler setup
```

### Running commands with secrets
```bash
# Instead of manually exporting env vars:
doppler run -- poe run

# Or inject into shell:
doppler run -- poetry shell
```

### Why Doppler?
- ✅ Secrets never committed to git
- ✅ Team sync without sharing `.env` files
- ✅ Audit logs and access control
- ✅ Multiple environments (dev, staging, prod)

**Never commit `.env` files or secrets to version control.**

## Code Style

- Format with `ruff format` before committing
- Lint with `ruff check` to catch issues
- Follow PEP 8, enforced by ruff configuration in `pyproject.toml`
- Maximum line length: 100 characters

## Commands Reference

```bash
poe test              # Run tests with coverage (min 80%)
poe lint              # Lint with ruff
poe format            # Format code with ruff
poe run               # Run CLI (requires env vars)
```
