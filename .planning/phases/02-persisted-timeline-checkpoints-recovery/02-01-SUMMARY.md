---
phase: 02-persisted-timeline-checkpoints-recovery
plan: 01
subsystem: storage
tags: [sqlalchemy, sqlite, postgresql, event-store, checkpoints, crash-recovery]

requires:
  - phase: 01-domain-models-state-machine-runtime
    provides: Domain models (Run, RunStatus, BudgetConfig) and StateMachine
provides:
  - "SQLAlchemy 2.0 models for runs, run_events, and checkpoints"
  - "Append-only EventRepository with monotonic sequence numbers and unique (run_id, sequence_no) constraint"
  - "CheckpointService for versioned state snapshots at safe execution boundaries"
  - "RecoveryService for restoring in-flight runs in fresh processes after crashes"
affects: [tools, approvals, api, demo]

actuals:
  tokens: 18000
  tasks: 3
  commits: 3

tech-stack:
  added: [sqlalchemy>=2.0, alembic>=1.13]
  patterns: [Repository pattern, Monotonic sequence generation, Fresh process crash recovery]

key-files:
  created:
    - src/agent_ops/storage/models.py
    - src/agent_ops/storage/database.py
    - src/agent_ops/storage/event_repository.py
    - src/agent_ops/storage/checkpoint_service.py
    - src/agent_ops/storage/recovery.py
    - tests/unit/test_storage_schema.py
    - tests/unit/test_event_service.py
    - tests/unit/test_checkpoint_recovery.py
  modified:
    - pyproject.toml
    - uv.lock
    - src/agent_ops/storage/__init__.py
    - src/agent_ops/runtime/engine.py

key-decisions:
  - "Use SQLAlchemy 2.0 Mapped type annotations and engine abstraction for PostgreSQL/SQLite compatibility"
  - "Monotonic event sequence numbers with database unique constraint on (run_id, sequence_no)"
  - "CheckpointService automatically synchronizes RunModel in database upon checkpoint creation"
  - "RecoveryService verifies run status and rejects resuming runs already in terminal states"

patterns-established:
  - "Monotonic sequence allocation via COALESCE(MAX(sequence_no), 0) + 1"
  - "Crash recovery emits a run.recovered event before handing execution back to WorkflowRuntime"

requirements-completed:
  - PERSIST-01
  - PERSIST-02
  - PERSIST-03
  - PERSIST-04

coverage:
  - id: D1
    description: "SQLAlchemy relational storage models for runs, run_events, and checkpoints"
    requirement: "PERSIST-04"
    verification:
      - kind: unit
        ref: "tests/unit/test_storage_schema.py"
        status: pass
  - id: D2
    description: "Append-only event log with monotonic sequence numbers and unique constraint"
    requirement: "PERSIST-01"
    verification:
      - kind: unit
        ref: "tests/unit/test_event_service.py"
        status: pass
  - id: D3
    description: "Versioned checkpoints and fresh-process restart recovery after simulated crashes"
    requirement: "PERSIST-02, PERSIST-03"
    verification:
      - kind: unit
        ref: "tests/unit/test_checkpoint_recovery.py"
        status: pass
---

# Phase 2 Plan 01 Summary: Persisted Timeline, Checkpoints & Recovery

Delivered the durable persistence layer for AgentOps: SQLAlchemy models, monotonic event timeline with database unique constraint enforcement, versioned checkpoints, and crash-restart recovery across process boundaries.

## Accomplishments

1. **SQLAlchemy Models & Engine (`PERSIST-04`):**
   - Configured SQLAlchemy 2.0+ and Alembic dependencies.
   - Defined `RunModel`, `RunEventModel`, and `CheckpointModel` with strict type annotations and foreign keys.
   - Configured database engine, table creation, and session context management.

2. **Event Repository & Monotonic Sequencing (`PERSIST-01`):**
   - Implemented `EventRepository.append_event` assigning monotonically increasing `sequence_no` (1, 2, 3...).
   - Enforced `UniqueConstraint("run_id", "sequence_no", name="uq_run_sequence")`.
   - Verified multi-run isolation and strict chronological event retrieval.

3. **Checkpoint Service & Process Restart Recovery (`PERSIST-02`, `PERSIST-03`):**
   - Implemented `CheckpointService` to save versioned serializable state snapshots and synchronize `RunModel`.
   - Implemented `RecoveryService.recover_run` to reconstruct domain `Run` instances from the latest checkpoint.
   - Verified restart recovery in a fresh process following a simulated mid-workflow crash.
   - Proved terminal runs (`SUCCEEDED`, `FAILED`, `CANCELLED`) reject resumption.

## Verification Results

- All 23 tests passing (`pytest`)
- 99% test coverage across `src/agent_ops` (`pytest-cov`)
- Strict static typing clean (`mypy`)
- Linting and formatting clean (`ruff`)
