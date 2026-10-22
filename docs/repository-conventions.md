# AgentOps Repository Conventions

## 1. Purpose

These conventions keep AgentOps maintainable, testable, secure, and consistent as the runtime, API, and dashboard evolve.

## 2. Package layout

- Application code lives in `src/agentops/`.
- Tests live in `tests/`.
- Unit tests live in `tests/unit/`.
- Integration tests live in `tests/integration/`.
- Contract tests live in `tests/contract/`.
- Architecture and engineering decisions are documented in `docs/`.
- CI workflows live in `.github/workflows/`.

Create modules when there is a real responsibility for them. Avoid unnecessary abstractions and empty packages.

## 3. Import conventions

- Use absolute imports beginning with `agentops`.
- Do not modify `sys.path` to make imports work.
- Keep imports at the top of a module unless a documented reason requires otherwise.
- Avoid circular imports. Move shared types to an appropriate lower-level module when necessary.
- Keep domain logic independent of FastAPI, database drivers, and external model providers.

Example:

    from agentops.domain.errors import InvalidTransitionError

## 4. Formatting and linting

- Use Ruff for formatting and linting.
- Maximum line length: 88 characters.
- Use four spaces for indentation and double quotes for Python strings.
- Sort imports automatically with Ruff.
- Fix lint issues rather than suppressing rules without justification.
- Any necessary suppression must be narrow and explain why it is required.

## 5. Typing

- Add type annotations to public functions, methods, and module-level interfaces.
- Use explicit return types.
- Prefer precise types over `Any`.
- Use `None` explicitly for optional values.
- Run mypy in strict mode for the application package.
- Avoid unvalidated casts and type ignores; document unavoidable cases.

## 6. Error handling

- Raise specific exceptions for expected domain failures.
- Define domain exceptions in the domain layer.
- Do not silently swallow exceptions.
- Catch exceptions only when the code can recover, add useful context, or translate them at a system boundary.
- Never expose secrets, credentials, raw internal stack traces, or sensitive tool output in API responses.
- Log useful diagnostic context without logging credentials or unnecessary personal data.
- Do not retry indefinitely. Retries must be bounded and appropriate for the operation.
- Never assume an external side effect did not occur merely because a response timed out.

## 7. Test conventions

- Use pytest.
- Name test files `test_*.py`.
- Name test functions `test_*`.
- Keep unit tests deterministic and independent of network access.
- Use synthetic fixtures for tickets, users, tools, and workflow events.
- Test both successful behavior and failure paths.
- Test authorization and safety boundaries, not only happy paths.
- Use integration tests when multiple components or persistence are involved.
- Do not require live model APIs, production credentials, or real external actions in the default test suite.
- Use explicit assertions; avoid tests that pass without checking behavior.

## 8. Runtime and safety conventions

- Lifecycle transitions must be explicit and validated.
- Persist approval decisions and checkpoint state before resuming protected workflow execution.
- Enforce reviewer authorization on the server side.
- Rejected or unapproved protected actions must not execute.
- Keep replay mode isolated from real external side effects.
- Apply step limits, timeouts, and bounded retry policies.
- Treat tool results, model outputs, and imported data as untrusted input.

## 9. Dependency management

- Declare project and development dependencies in `pyproject.toml`.
- Commit `uv.lock`.
- Use `uv sync --locked` in CI to prevent accidental lockfile drift.
- Do not commit `.venv`, `.env`, credentials, local databases, or generated test reports.
- Update dependencies intentionally and review lockfile changes.

## 10. Pull request and CI requirements

Before merging, the following checks must pass:

1. Ruff lint.
2. Ruff format check.
3. Strict mypy check.
4. pytest test suite.
5. Dependency lockfile validation.

Changes to workflow safety, persistence, approval, or recovery should include targeted regression tests.

## 11. Naming

- Modules and functions: `snake_case`.
- Classes and exceptions: `PascalCase`.
- Constants: `UPPER_SNAKE_CASE`.
- Test names should describe behavior, for example `test_rejected_approval_does_not_execute_action`.

## 12. Design principle

Prefer simple, explicit, testable code. Do not introduce a framework, abstraction, dependency, or distributed component unless it solves a demonstrated requirement.
