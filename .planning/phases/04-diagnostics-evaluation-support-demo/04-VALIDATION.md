# Phase 4: Diagnostics, Evaluation & Support Demo - Validation Plan

## Test Execution Commands

```bash
# Run unit tests for Phase 4
uv run pytest tests/unit/test_redaction_capsules.py tests/unit/test_mock_replay.py tests/unit/test_evaluator.py tests/unit/test_support_workflow.py

# Run API integration tests
uv run pytest tests/integration/test_api_endpoints.py

# Full test suite with coverage
uv run pytest --cov=agent_ops

# Strict type checking
uv run mypy

# Linting and formatting
uv run ruff check .
uv run ruff format --check .
```

## Validation Matrix

| Requirement | Target Component | Verification Kind | Test File |
|-------------|------------------|-------------------|-----------|
| `DIAG-01` | Redactor & FailureCapsule | Unit | `tests/unit/test_redaction_capsules.py` |
| `DIAG-02` | MockReplayRunner | Unit | `tests/unit/test_mock_replay.py` |
| `DIAG-03` | TrajectoryEvaluator | Unit | `tests/unit/test_evaluator.py` |
| `DEMO-01` | SupportTriageWorkflow | Unit / Functional | `tests/unit/test_support_workflow.py` |
| `API-01` | FastAPI Control Endpoints | Integration | `tests/integration/test_api_endpoints.py` |

## Acceptance Criteria
1. Seeded secrets (API keys, tokens, authorization headers) in inputs, state, tool args, or events are completely replaced with `[REDACTED]` in exported capsules.
2. Mock replay reproduces workflow execution using only recorded data, making 0 external socket/network calls.
3. Trajectory evaluation detects skipped approvals, forbidden steps, and policy breaches.
4. Support triage workflow executes end-to-end: pause on T2 draft, resume on approved, cancel on rejected.
5. FastAPI endpoints handle all lifecycle actions, return stable error codes, and support idempotent run creation.
