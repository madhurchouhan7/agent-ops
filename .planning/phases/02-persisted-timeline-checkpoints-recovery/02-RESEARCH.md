# Phase 2: Persisted Timeline, Checkpoints & Recovery — Research

**Phase:** 02  
**Status:** Complete  
**Date:** 2026-10-22  
**Target:** Durable PostgreSQL Storage, Monotonic Event Sequences, Versioned Checkpoints, and Restart Recovery

## User Constraints

### Locked Decisions
- **Relational Storage**: PostgreSQL as production target datastore; SQLAlchemy 2.0+ as ORM/repository layer, and Alembic for repeatable schema migrations [VERIFIED: docs/07-technology-stack.md:9-11].
- **Event Ordering**: Monotonic `sequence_no` per run with a strict database unique constraint on `(run_id, sequence_no)`. Do not rely solely on timestamps for ordering [VERIFIED: docs/06-system-design.md:10].
- **Event Immutability**: `run_events` is append-only. Events are never updated or deleted in place [VERIFIED: docs/08-data-model.md:29].
- **Checkpoint Boundaries**: Versioned snapshots saved at documented safe boundaries. Checkpoints must be serializable and contain approved state fields only [VERIFIED: docs/11-runtime-rules.md:20-21].
- **Restart Recovery**: A fresh process must be able to restore an in-flight run from its latest checkpoint and resume execution cleanly [VERIFIED: docs/01-mvp-contract.md:70].
- **Testing Standard**: Deterministic unit and integration tests with synthetic fixtures; zero live external network dependencies required [VERIFIED: docs/repository-conventions.md:65-70]. Supports SQLite in tests for fast local runs while preserving PostgreSQL compatibility.

## Standard Stack

| Role | Selection | Rationale |
|---|---|---|
| ORM / Persistence | `SQLAlchemy>=2.0` | Modern 2.0 type-annotated Mapped columns (`Mapped[str]`), cross-database dialect compatibility, clean transaction handling. |
| Schema Migrations | `Alembic>=1.13` | Deterministic, versioned schema evolution. |
| Database Engine | PostgreSQL (prod) / SQLite (tests) | PostgreSQL enforces constraints in production; SQLite enables instant, zero-docker unit/integration testing in CI. |
| Data Validation | `Pydantic v2` | Validates serializable state payloads before saving into JSON columns. |

## Architecture Patterns

### 1. Database Schema (`docs/08-data-model.md`)

```sql
-- runs table
CREATE TABLE runs (
    id VARCHAR(64) PRIMARY KEY,
    workflow_id VARCHAR(128) NOT NULL,
    workflow_version VARCHAR(32) NOT NULL DEFAULT '1.0',
    status VARCHAR(32) NOT NULL,
    current_node VARCHAR(128),
    step_count INTEGER NOT NULL DEFAULT 0,
    state_json JSON NOT NULL DEFAULT '{}',
    budget_json JSON NOT NULL DEFAULT '{}',
    error_code VARCHAR(64),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);

-- run_events table (append-only)
CREATE TABLE run_events (
    id VARCHAR(64) PRIMARY KEY,
    run_id VARCHAR(64) NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
    sequence_no INTEGER NOT NULL,
    event_type VARCHAR(64) NOT NULL,
    node_id VARCHAR(128),
    payload_json JSON NOT NULL DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    CONSTRAINT uq_run_sequence UNIQUE (run_id, sequence_no)
);

-- checkpoints table
CREATE TABLE checkpoints (
    id VARCHAR(64) PRIMARY KEY,
    run_id VARCHAR(64) NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
    sequence_no INTEGER NOT NULL,
    schema_version VARCHAR(32) NOT NULL DEFAULT '1.0',
    state_json JSON NOT NULL DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL
);
```

### 2. Monotonic Event Sequencing
To guarantee strict event ordering:
1. Within a database transaction, lock the run or query `COALESCE(MAX(sequence_no), 0) + 1` for the given `run_id`.
2. Insert into `run_events`.
3. If concurrent step executions attempt to write the same `sequence_no`, the database unique constraint `(run_id, sequence_no)` rejects the duplicate with an `IntegrityError`, enforcing monotonic ordering.

### 3. Checkpoint & Restart Recovery Protocol
When an unexpected crash or process restart occurs:
1. The recovery service queries the database for the run: `SELECT * FROM runs WHERE id = :run_id`.
2. If `run.status` is terminal (`SUCCEEDED`, `FAILED`, `CANCELLED`), recovery rejects resumption.
3. If `run.status` is `PAUSED` or `RUNNING` (interrupted in-flight):
   - Fetch the latest checkpoint: `SELECT * FROM checkpoints WHERE run_id = :run_id ORDER BY sequence_no DESC LIMIT 1`.
   - Restore the runtime `Run` object using the checkpoint's `state_json` and `sequence_no`.
   - Append a `run.recovered` event to `run_events`.
   - Hand the restored `Run` back to `WorkflowRuntime` to safely continue execution.

## Don't Hand-Roll
- Do not concatenate raw SQL strings; use SQLAlchemy `select()`, `insert()`, and parameterized queries.
- Do not generate migration scripts manually; use Alembic.
- Do not generate non-standard UUID formats; use `uuid.uuid4().hex` for record IDs.

## Common Pitfalls
1. **Timestamp-only ordering**: Timestamps can collide or skew across distributed clocks. The database `sequence_no` constraint `(run_id, sequence_no)` is the authoritative order.
2. **Crash between side effect and checkpoint**: Record the event and checkpoint atomically in the same transaction where feasible.
3. **Storing un-sanitized credentials in state or events**: Strip or reject any credentials before serialization.
4. **Resuming terminal runs**: Recovery must fail closed if a run has already completed or been cancelled.
