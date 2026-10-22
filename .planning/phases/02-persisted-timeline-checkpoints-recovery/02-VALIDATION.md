---
phase: "2"
slug: "persisted-timeline-checkpoints-recovery"
status: draft
nyquist_compliant: true
wave_0_complete: false
created: "2026-10-22"
---

# Phase 2 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.3+ / pytest-cov 5.0+ |
| **Config file** | `pyproject.toml` |
| **Quick run command** | `uv run pytest tests/unit/test_storage.py` |
| **Full suite command** | `uv run pytest --cov=agent_ops` |
| **Estimated runtime** | ~2 seconds |

---

## Sampling Rate

- **After every task commit:** Run `uv run pytest tests/unit/`
- **After every plan wave:** Run `uv run pytest --cov=agent_ops` and `uv run mypy`
- **Before `/gsd-verify-work`:** Full test suite and strict mypy must be 100% green
- **Max feedback latency:** 5 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 02-01-01 | 01 | 1 | PERSIST-04 | — | SQLAlchemy tables and Alembic configuration match spec | unit | `uv run pytest tests/unit/test_storage_schema.py` | ❌ W0 | ⬜ pending |
| 02-01-02 | 01 | 1 | PERSIST-01 | T-02-01 | Monotonic sequence constraint and append-only event log | unit | `uv run pytest tests/unit/test_event_service.py` | ❌ W0 | ⬜ pending |
| 02-01-03 | 01 | 1 | PERSIST-02, PERSIST-03 | T-02-02 | Checkpoint saving and clean restart recovery in fresh process | unit | `uv run pytest tests/unit/test_checkpoint_recovery.py` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/unit/test_storage_schema.py` — verifies SQLAlchemy schema models and constraints
- [ ] `tests/unit/test_event_service.py` — verifies monotonic sequence numbers and unique constraint
- [ ] `tests/unit/test_checkpoint_recovery.py` — verifies checkpoint creation and crash recovery

---

## Manual-Only Verifications

None — Phase 2 persistence, constraints, and recovery are 100% automated with deterministic tests.
