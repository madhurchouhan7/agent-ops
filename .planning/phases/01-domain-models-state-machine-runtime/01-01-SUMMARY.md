---
phase: 01-domain-models-state-machine-runtime
plan: 01
subsystem: runtime
tags: [state-machine, fsm, pydantic, runtime, budgets]

requires: []
provides:
  - "Core domain models (Run, RunStatus, Step, BudgetConfig)"
  - "Domain exceptions (InvalidTransitionError, TerminalStateError, BudgetExceededError)"
  - "Explicit Finite State Machine and transition validator with terminal state protection"
  - "Bounded step execution runtime engine with max_steps and wall-clock timeout budgets"
affects: [persistence, tools, approvals, evaluation]

actuals:
  tokens: 12500
  tasks: 3
  commits: 2

tech-stack:
  added: [pydantic>=2.7]
  patterns: [Explicit FSM transition matrix, Bounded step execution loop]

key-files:
  created:
    - src/agent_ops/domain/errors.py
    - src/agent_ops/domain/models.py
    - src/agent_ops/domain/state_machine.py
    - src/agent_ops/runtime/engine.py
    - tests/unit/test_domain_models.py
    - tests/unit/test_state_machine.py
    - tests/unit/test_runtime_budgets.py
  modified:
    - pyproject.toml
    - uv.lock
    - src/agent_ops/domain/__init__.py
    - src/agent_ops/runtime/__init__.py

key-decisions:
  - "Use Pydantic v2 for immutable domain models with strict UTC datetime defaults"
  - "Explicit FSM transition matrix checking terminal states (SUCCEEDED, FAILED, CANCELLED) before any state transition"
  - "Enforce max_steps and wall-clock execution budgets before each node execution step in the runtime engine"

patterns-established:
  - "TerminalStateError on any transition attempt from terminal states"
  - "BudgetExceededError halts runaway execution and marks run as FAILED"

requirements-completed:
  - STATE-01
  - STATE-02
  - STATE-03

coverage:
  - id: D1
    description: "Domain models for RunStatus, Run, Step, and BudgetConfig with strict validation"
    requirement: "STATE-01"
    verification:
      - kind: unit
        ref: "tests/unit/test_domain_models.py"
        status: pass
  - id: D2
    description: "State machine with transition matrix and terminal state protection"
    requirement: "STATE-02"
    verification:
      - kind: unit
        ref: "tests/unit/test_state_machine.py"
        status: pass
  - id: D3
    description: "Bounded step runtime with step counter and timeout budget guards"
    requirement: "STATE-03"
    verification:
      - kind: unit
        ref: "tests/unit/test_runtime_budgets.py"
        status: pass
---

# Phase 1 Plan 01 Summary: Domain Models & State Machine Runtime

Delivered the Walking Skeleton for AgentOps: core domain models, explicit finite state machine with terminal state enforcement, and a bounded in-memory runtime execution engine with step count and timeout budget guards.

## Accomplishments

1. **Domain Models & Enums (`STATE-01`):**
   - Implemented `RunStatus` (`CREATED`, `RUNNING`, `PAUSED`, `SUCCEEDED`, `FAILED`, `CANCELLED`).
   - Implemented `TERMINAL_STATUSES` set (`SUCCEEDED`, `FAILED`, `CANCELLED`).
   - Implemented `BudgetConfig`, `Step`, and `Run` Pydantic models with UTC-aware timestamps and strict validation.
   - Defined domain exceptions hierarchy (`AgentOpsError`, `InvalidTransitionError`, `TerminalStateError`, `BudgetExceededError`, `ValidationError`).

2. **State Machine & Transition Matrix (`STATE-02`):**
   - Implemented `StateMachine` with explicit `ALLOWED_TRANSITIONS` matrix.
   - Guaranteed that terminal states can never be transitioned out of (`TerminalStateError`).
   - Verified 100% of the 36 status transition permutations via an exhaustive unit test suite.

3. **Bounded Step Runtime & Budget Guard (`STATE-03`):**
   - Implemented `WorkflowRuntime` with bounded `execute_step`.
   - Enforced `max_steps` and `timeout_seconds` budgets, halting runaway loops with `BUDGET_EXCEEDED` and setting run status to `FAILED`.
   - Implemented pause, resume, cancel, complete, and fail helpers.
   - Verified end-to-end multi-step happy path from `CREATED` -> `RUNNING` -> `PAUSED` -> `RUNNING` -> `SUCCEEDED`.

## Verification Results

- All 14 tests passing (`pytest`)
- 99% test coverage across `src/agent_ops` (`pytest-cov`)
- Strict type checking clean (`mypy`)
- Formatting and linting clean (`ruff`)
