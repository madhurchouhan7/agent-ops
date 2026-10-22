# Synthesized Decisions

## ADR-001: Technology Stack and Role
- source: docs/07-technology-stack.md
- status: locked (Accepted)
- decision: Use Python 3.11+, Pydantic for schema validation, pytest for deterministic tests, FastAPI for REST control API, PostgreSQL with SQLAlchemy and Alembic for durable persistence, Next.js with TypeScript for the web console. Use mocked models for deterministic testing; keep dependencies lean and pin versions.
- scope: Python 3.11+, FastAPI, PostgreSQL, Pydantic, SQLAlchemy, Alembic, Next.js, pytest

## ADR-002: Repository and Engineering Conventions
- source: docs/repository-conventions.md
- status: locked (Accepted)
- decision: Structure application code under src/agentops (or agent_ops), strictly enforce mypy in strict mode, use Ruff for linting and formatting with 88-char limit, write deterministic unit tests without network access, test failure and security paths, enforce authorization and safety in code outside prompts, and require clean CI passing lint, format, strict mypy, and coverage.
- scope: Package Layout, Import Conventions, Ruff, Mypy Strict, Pytest, Runtime Safety Conventions

## ADR-003: Replay and Failure Capsule Isolation
- source: docs/05-architecture.md
- status: locked (Accepted)
- decision: Replay mode must be mock-only/read-only by default and make zero external network requests or side effects. Failure capsules must strip/redact all credentials and secrets before export.
- scope: Replay, Failure Capsule, Mock Mode, Redaction
