# Phase 1: Domain Models & State Machine Runtime — Research

**Phase:** 01  
**Status:** Complete  
**Date:** 2026-10-22  
**Target:** Walking Skeleton for In-Memory State Machine and Bounded Execution Runtime

## User Constraints

### Locked Decisions
- **Programming Language & Version**: Python 3.11+ [VERIFIED: pyproject.toml:10]
- **Validation & Models**: Pydantic v2 (or Python `dataclasses` / `Enum` with strict Pydantic models for serialization) [VERIFIED: docs/07-technology-stack.md:6]
- **Lifecycle Statuses**: Exactly six lifecycle states: `CREATED`, `RUNNING`, `PAUSED`, `SUCCEEDED`, `FAILED`, `CANCELLED`. Terminal states are `SUCCEEDED`, `FAILED`, and `CANCELLED` [VERIFIED: docs/01-mvp-contract.md:28-37].
- **Error Categories**: Specific domain error types: `InvalidTransitionError`, `TerminalStateError`, `BudgetExceededError`, `ValidationError` [VERIFIED: docs/11-runtime-rules.md:47].
- **Budgets**: Explicit maximum step count and execution timeout constraints per run [VERIFIED: docs/11-runtime-rules.md:12-14].
- **Testing Standard**: pytest with deterministic synthetic tests and zero live external network dependencies [VERIFIED: docs/repository-conventions.md:65-70].

## Standard Stack

| Role | Selection | Rationale |
|---|---|---|
| Domain Models | `pydantic.BaseModel` / `enum.StrEnum` | Immutable/strict schema validation, native JSON serialization, strict typing support. |
| State Machine | Explicit transition table / Finite State Machine pattern | Direct mapping from `(current_status, target_status) -> allowed_nodes/actions`. Simple, transparent, and avoids heavy third-party state machine dependencies. |
| Time Tracking | Standard library `datetime` with `timezone.utc` | Clean, monotonic timestamps without external timezone dependencies. |
| Test Runner | `pytest` + `pytest-cov` | Enforces 100% legal and illegal transition testing. |

## Architecture Patterns

### 1. State Machine & Transition Matrix
The state machine governs the lifecycle status of a `Run`:
```
[CREATED] ---> [RUNNING] <---> [PAUSED]
                  |
                  v (Terminal)
       [SUCCEEDED | FAILED | CANCELLED]
```

- **Valid Transitions**:
  - `CREATED` -> `RUNNING`, `CANCELLED`
  - `RUNNING` -> `PAUSED`, `SUCCEEDED`, `FAILED`, `CANCELLED`
  - `PAUSED` -> `RUNNING`, `CANCELLED`
  - `SUCCEEDED`, `FAILED`, `CANCELLED` -> No outgoing transitions allowed (`TerminalStateError`).

### 2. Separation of Lifecycle Status vs Current Node
As mandated by UX and architecture rules [VERIFIED: docs/01-mvp-contract.md:37], `status` (e.g. `RUNNING`, `PAUSED`) is strictly separate from `current_node` (e.g. `classify_ticket`, `lookup_ticket`, `draft_response`).

### 3. Step Execution Loop and Budgets
The execution engine runs bounded steps:
- Each step increments `step_count`.
- If `step_count > max_steps`, the run immediately halts with `BudgetExceededError` and transitions status to `FAILED`.
- If wall-clock elapsed time exceeds `timeout_seconds`, the run halts and transitions status to `FAILED`.

## Don't Hand-Roll
- Do not create custom regex-based JSON parsers; use Pydantic models with `model_validate` and `model_dump`.
- Do not use naive mutable default arguments (e.g. `state: dict = {}`); use Pydantic `Field(default_factory=dict)`.
- Do not mutate terminal state in place without going through transition validation.

## Common Pitfalls
1. **Allowing resumption from terminal states**: Any transition attempt on a run whose status is already in `[SUCCEEDED, FAILED, CANCELLED]` must raise `TerminalStateError`.
2. **Infinite loops**: Without a strict step counter check *before* executing the next node, a circular graph can lock the process.
3. **Timezone bugs**: Ensure all timestamps are UTC-aware (`datetime.now(timezone.utc)`).
4. **Leaking internal tracebacks in error responses**: Use structured domain exceptions (`AgentOpsError` base class).

## Code Patterns

```python
from enum import StrEnum
from pydantic import BaseModel, Field
from datetime import datetime, timezone


class RunStatus(StrEnum):
    CREATED = "CREATED"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


TERMINAL_STATUSES = {RunStatus.SUCCEEDED, RunStatus.FAILED, RunStatus.CANCELLED}

ALLOWED_TRANSITIONS: dict[RunStatus, set[RunStatus]] = {
    RunStatus.CREATED: {RunStatus.RUNNING, RunStatus.CANCELLED},
    RunStatus.RUNNING: {
        RunStatus.PAUSED,
        RunStatus.SUCCEEDED,
        RunStatus.FAILED,
        RunStatus.CANCELLED,
    },
    RunStatus.PAUSED: {RunStatus.RUNNING, RunStatus.CANCELLED},
    RunStatus.SUCCEEDED: set(),
    RunStatus.FAILED: set(),
    RunStatus.CANCELLED: set(),
}
```
