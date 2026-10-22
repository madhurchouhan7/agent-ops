# Walking Skeleton — AgentOps

**Phase:** 1  
**Generated:** 2026-10-22  

## Capability Proven End-to-End

A developer can initialize a stateful AI workflow run, execute bounded in-memory state transitions with strict step budgets, and enforce valid lifecycle state progressions (`CREATED` -> `RUNNING` -> `SUCCEEDED` / `FAILED` / `CANCELLED`).

## Architectural Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Language & Runtime | Python 3.11+ | High performance, native StrEnum and modern typing, strict static analysis. |
| Domain Models | Pydantic v2 `BaseModel` | Strict runtime validation, immutability guarantees, and standard JSON export. |
| State Machine Architecture | Explicit Transition Matrix & FSM | Simple, verifiable, zero external dependencies, robust terminal state protection. |
| Package Structure | `src/agent_ops/domain/` & `src/agent_ops/runtime/` | Clean separation between pure domain rules and runtime execution engine. |
| Typing & Linting | Strict mypy + Ruff | Zero type errors (`strict = true`), consistent 88-char formatting. |
| Testing Engine | pytest + coverage | Deterministic unit tests with fast feedback latency (<1s). |

## Stack Touched in Phase 1

- [x] Project scaffold (pyproject.toml, ruff, strict mypy, pytest)
- [ ] Domain models (`RunStatus`, `Run`, `Step`, `TransitionRule`, `BudgetConfig`)
- [ ] State Machine transition validation logic (legal transitions, terminal state enforcement)
- [ ] Bounded Runtime execution loop (step counter limits, wall-clock timeout checks)
- [ ] Unit test suite covering 100% of legal and illegal transition combinations

## Out of Scope (Deferred to Later Slices)

- PostgreSQL persistence and migrations (Deferred to Phase 2)
- Monotonic append-only database event tables (Deferred to Phase 2)
- Tool registry and external tool adapters (Deferred to Phase 3)
- Policy gate and human approval pause/resume (Deferred to Phase 3)
- FastAPI REST endpoints and web console (Deferred to Phase 4)
- Redacted Failure Capsules and offline mock replay (Deferred to Phase 4)

## Subsequent Slice Plan

- **Phase 2:** Durable persistence layer with PostgreSQL, append-only `run_events`, versioned checkpoints, and crash-restart recovery.
- **Phase 3:** Tool registry with schema validation, risk tiers (`T0`-`T3`), code-level policy gate, and human-in-the-loop approvals.
- **Phase 4:** Failure capsule export, offline mock replay, golden trajectory CI suite, and the end-to-end support triage demo.
