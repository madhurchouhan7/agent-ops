# Phase 3: Tool Registry, Policy Gate & Approvals — Research

**Phase:** 03  
**Status:** Complete  
**Date:** 2026-10-22  
**Target:** Allow-listed Tool Registry, Code-Enforced Policy Gate, Risk Tiers (T0-T3), and Human-in-the-Loop Approvals

## User Constraints

### Locked Decisions
- **Code-Level Policy Enforcement**: Policy checks, argument validation, and authorization must be evaluated in code outside model prompts. System prompts are not security boundaries [VERIFIED: docs/10-security-and-threat-model.md:14].
- **Allow-Listed Tools**: Model outputs cannot invoke arbitrary Python functions, host executables, or shell commands. Only allow-listed, registered tools with strict schemas can execute [VERIFIED: docs/11-runtime-rules.md:9-10].
- **Fail Closed**: Unknown, unauthorized, or malformed tool invocations must fail closed and never execute [VERIFIED: docs/11-runtime-rules.md:12].
- **Risk Tiers**:
  - `T0`: Local deterministic fixtures / read-only local data.
  - `T1`: Read-only external query with scoped credentials.
  - `T2`: Reversible write; requires human approval and idempotency.
  - `T3`: High-impact/irreversible; strictly disabled in V1 [VERIFIED: docs/10-security-and-threat-model.md:26-29].
- **Human Approval & Rejection Invariant**:
  - Protected actions (`T2`, such as `send_reply`) automatically pause the run and persist an approval record.
  - Server-side authorization check ensures only authorized reviewers can submit decisions.
  - Rejection guarantees that the protected action is NEVER executed [VERIFIED: docs/11-runtime-rules.md:27, 38].
  - Approval state survives process restarts [VERIFIED: docs/01-mvp-contract.md:69].

## Standard Stack

| Role | Selection | Rationale |
|---|---|---|
| Schema Validation | Pydantic v2 `BaseModel` | Strict typing and validation of tool input/output payloads. |
| Tool Registry | Custom Registry Pattern | Explicit allow-list mapping tool names to schemas, handlers, timeouts, and risk tiers. |
| Policy Gate | Code-enforced evaluator | Evaluates tool permissions, schemas, and risk tiers prior to invocation. |
| Persistence | SQLAlchemy `ApprovalModel` | Relational table storing approval requests, reviewer identities, and audit decisions. |

## Architecture Patterns

### 1. Tool Registry & Schema Contract

```python
class RiskTier(StrEnum):
    T0 = "T0"  # Read-only deterministic fixtures
    T1 = "T1"  # Read-only external queries
    T2 = "T2"  # Reversible writes requiring approval
    T3 = "T3"  # High-impact/irreversible (disabled in V1)


class ToolDefinition(BaseModel):
    name: str
    description: str
    version: str = "1.0"
    risk_tier: RiskTier
    input_schema: type[BaseModel]
    timeout_seconds: float = 10.0
```

### 2. Policy Gate Evaluation Sequence

```
Proposed Tool Call -> PolicyGate.evaluate()
                           |
            +--------------+--------------+
            |                             |
      Invalid / Unknown             Valid Tool
            |                             |
     [FAIL CLOSED]                  Risk Tier Check
  (POLICY_DENIED error)                   |
                               +----------+----------+
                               |                     |
                            T0 / T1                  T2
                               |                     |
                           [EXECUTE]          [REQUIRE APPROVAL]
                                                     |
                                            Pause Run & Persist
                                            ApprovalRequest
```

### 3. Approval Lifecycle & Safety Guarantee

- **Pending**: Run enters `PAUSED` state. Approval record created in `approvals` table.
- **Decision Submission**:
  - Validates reviewer identity and authorization role (`reviewer` or `admin`).
  - If **Approved**: Run can be resumed by `WorkflowRuntime`, and the protected tool action executes.
  - If **Rejected**: Approval status marked `REJECTED`, run status transitions to `CANCELLED` (or terminal rejection), and the protected tool action is guaranteed never to execute.

## Don't Hand-Roll
- Do not inspect system prompt strings to check permissions; check tool schemas and risk tiers directly in Python code.
- Do not execute tool handlers in an un-timed loop; enforce `timeout_seconds`.
- Do not trust tool output; validate output schemas before merging into run state.

## Common Pitfalls
1. **Bypassing approval on resume**: Calling `runtime.resume(run)` must not execute the protected action unless an `APPROVED` approval record exists for that run and action.
2. **Reviewer spoofing**: Authorize reviewer roles on the server side; never trust a client-supplied flag without checking permissions.
3. **Rejection executing side effects**: Ensure the rejection handler terminates or skips the protected node completely.
