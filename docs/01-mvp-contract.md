# AOPS-001 — AgentOps MVP Contract

**Status:** Proposed baseline for implementation  
**Version:** 0.1  
**Last updated:** 2026-10-21

## Product statement
AgentOps is a developer control plane for running, inspecting, and recovering stateful AI workflows. V1 prioritizes one reliable, observable workflow—not a general-purpose autonomous platform.

## Primary user story
> As a developer building tool-using AI workflows, I want to execute a workflow with explicit state transitions, inspect its event history, recover from a saved checkpoint, and pause for human approval before a protected action, so that I can debug failures and demonstrate controlled execution rather than relying on opaque chat loops.

## V1 demo workflow
1. Submit a synthetic support ticket.
2. Create a run and record `run.created`.
3. Classify category/urgency using deterministic fixtures or a mocked model adapter.
4. Call an allow-listed `lookup_ticket` tool against synthetic data.
5. Draft a suggested response.
6. Pause before a simulated `send_reply` action because policy requires approval.
7. Persist the paused state and pending approval.
8. An authorized reviewer approves or rejects.
9. If approved, resume and simulate sending; if rejected, never execute the protected action.
10. Show status, current node, event timeline, tool outcomes, and decision in the dashboard.
11. Inject a failure, export a redacted Failure Capsule, and replay recorded outputs in mock mode.

## Supported lifecycle states

| State | Meaning | Terminal? |
|---|---|---:|
| `CREATED` | Run exists but has not started | No |
| `RUNNING` | Runtime may execute the next permitted step | No |
| `PAUSED` | Waiting for an explicit resume/approval event | No |
| `SUCCEEDED` | Workflow completed successfully | Yes |
| `FAILED` | Unrecoverable failure or policy exhausted | Yes |
| `CANCELLED` | Run was cancelled and cannot continue | Yes |

Terminal states are `SUCCEEDED`, `FAILED`, and `CANCELLED`. A terminal run cannot be resumed; create a new run for another attempt. Lifecycle status is separate from `current_node`; a run may be `RUNNING` at node `lookup_ticket`.

## V1 must-have scope
- Explicit graph/state machine and bounded step execution.
- Validated run state and workflow input.
- Bounded retry of classified transient failures.
- Persisted event timeline and versioned checkpoints.
- Restart recovery from documented safe boundaries.
- Allow-listed tools with strict schemas and policy checks.
- Pause/resume and approval decisions.
- FastAPI endpoints and PostgreSQL persistence for runs, events, checkpoints, approvals.
- Web console for runs, timeline, safe state view, and approvals.
- Redacted Failure Capsule export and mock-only replay.
- Unit, integration, security, and trajectory tests.
- Reproducible local setup and demo.

## Explicitly out of scope
- General-purpose visual workflow builder.
- Arbitrary code/shell execution on the host.
- Live email sending, payments, production database writes, or destructive actions.
- Unrestricted autonomous planning or unbounded loops.
- Full multi-agent swarm orchestration.
- Broad support for arbitrary MCP servers.
- Distributed multi-worker durability guarantees in the first release.
- Kubernetes, billing, enterprise SSO, or hosted SaaS launch.
- Exactly-once execution guarantees for arbitrary external systems.

## MVP success criteria
- [ ] Clean local setup runs the synthetic demo end to end.
- [ ] Legal transitions succeed; illegal transitions are rejected.
- [ ] Retry attempts and workflow steps are bounded.
- [ ] Paused runs cannot advance without a valid decision.
- [ ] Approval survives process restart and is authorization-checked.
- [ ] A fresh process restores a checkpoint using a documented test.
- [ ] Event history shows lifecycle and tool outcomes in order.
- [ ] Failure Capsule omits seeded secret values.
- [ ] Mock replay performs no external calls or side effects.
- [ ] Golden trajectory tests catch skipped safety steps.
- [ ] API/UI errors do not leak secrets or stack traces.
- [ ] Setup, tests, limitations, and demo instructions are documented.

## Metrics to measure, not invent
- Success rate on a fixed synthetic test set.
- Policy violation count.
- Recovery success rate after injected failures.
- Retry distribution and p50/p95 duration.
- Failure diagnosis time.
- Capsule redaction test pass rate.

## AOPS-001 completion record
- [x] Primary user story written.
- [x] Demo workflow written.
- [x] Lifecycle and terminal states defined.
- [x] Non-goals documented.
- [x] Measurable success criteria documented.

**Next:** AOPS-002 — initialize the Git repository, `.gitignore`, and first documentation commit.
