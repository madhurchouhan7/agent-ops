---
phase: "3"
slug: "tool-registry-policy-gate-approvals"
status: draft
nyquist_compliant: true
wave_0_complete: false
created: "2026-10-22"
---

# Phase 3 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.3+ / pytest-cov 5.0+ |
| **Config file** | `pyproject.toml` |
| **Quick run command** | `uv run pytest tests/unit/test_tools.py tests/unit/test_approvals.py` |
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
| 03-01-01 | 01 | 1 | TOOL-01, TOOL-03 | T-03-01 | Allow-list registration, input validation, unknown tool rejection | unit | `uv run pytest tests/unit/test_tool_registry.py` | ❌ W0 | ⬜ pending |
| 03-01-02 | 01 | 1 | TOOL-02 | T-03-02 | Risk tier gating (T0-T3) and policy evaluation outside prompts | unit | `uv run pytest tests/unit/test_policy_gate.py` | ❌ W0 | ⬜ pending |
| 03-01-03 | 01 | 1 | HITL-01, HITL-02, HITL-03 | T-03-03 | Approval creation, reviewer auth, and rejection blocking execution | unit | `uv run pytest tests/unit/test_approvals.py` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/unit/test_tool_registry.py` — tests tool allow-list, schema validation, and timeouts
- [ ] `tests/unit/test_policy_gate.py` — tests risk tiers T0-T3, T3 disabling, and permission checks
- [ ] `tests/unit/test_approvals.py` — tests approval lifecycle, restart persistence, and rejection safety guarantee

---

## Manual-Only Verifications

None — Phase 3 tool policy gates and approval logic are 100% automated with deterministic tests.
