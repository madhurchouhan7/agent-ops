---
phase: "1"
slug: "domain-models-state-machine-runtime"
status: draft
nyquist_compliant: true
wave_0_complete: false
created: "2026-10-22"
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.3+ / pytest-cov 5.0+ |
| **Config file** | `pyproject.toml` |
| **Quick run command** | `uv run pytest tests/unit/test_state_machine.py` |
| **Full suite command** | `uv run pytest --cov=agent_ops` |
| **Estimated runtime** | ~1 second |

---

## Sampling Rate

- **After every task commit:** Run `uv run pytest tests/unit/`
- **After every plan wave:** Run `uv run pytest --cov=agent_ops` and `uv run mypy`
- **Before `/gsd-verify-work`:** Full suite and strict mypy must be 100% green
- **Max feedback latency:** 5 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 01-01-01 | 01 | 1 | STATE-01 | — | Enum and schema definitions match specification | unit | `uv run pytest tests/unit/test_domain_models.py` | ❌ W0 | ⬜ pending |
| 01-01-02 | 01 | 1 | STATE-01, STATE-02 | T-01-01 | Transitions validated; terminal states reject transitions | unit | `uv run pytest tests/unit/test_state_machine.py` | ❌ W0 | ⬜ pending |
| 01-01-03 | 01 | 1 | STATE-03 | T-01-02 | Step counter and timeouts enforce budget halts | unit | `uv run pytest tests/unit/test_runtime_budgets.py` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/unit/test_domain_models.py` — unit tests for RunStatus, Run, Step, and transition validation
- [ ] `tests/unit/test_state_machine.py` — matrix tests for all legal/illegal state machine transitions
- [ ] `tests/unit/test_runtime_budgets.py` — tests for step limit and timeout budgets

---

## Manual-Only Verifications

None — Phase 1 core domain logic is 100% automated and deterministic.
