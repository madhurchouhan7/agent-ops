# Security and Threat Model

## Assets
Inputs, workflow state, credentials, tool capabilities, events/checkpoints/capsules, approval records, database and workspace boundaries.

## Threats
Direct/indirect prompt injection; poisoned tool descriptions; unauthorized tool calls; cross-workspace access; secret leakage; duplicate side effects; runaway loops/resource exhaustion; malicious code execution.

## Required controls
1. Authenticate callers.
2. Authorize every resource access server-side.
3. Give tools least privilege.
4. Allow-list tools and validate schemas.
5. Enforce policy in code, not only in model prompts.
6. Treat model output, retrieved content, and tool results as untrusted.
7. Cap steps, retries, runtime, payload/output sizes, and spending where available.
8. Redact before logging/persisting/exporting.
9. Keep credentials outside state and source control.
10. Require approval for designated risky actions.
11. Use idempotency and explicit unknown-outcome handling.
12. Never run arbitrary code on the application host.
13. Define retention/deletion for run data.
14. Audit policy and approval decisions.

## Risk tiers
- `T0`: local deterministic fixtures/read-only local data.
- `T1`: read-only external query with scoped credentials.
- `T2`: reversible write; approval/idempotency required.
- `T3`: high-impact/irreversible; disabled in V1.

## Security tests
- Unknown tool rejected.
- Invalid/oversized arguments rejected.
- Cross-user run access denied.
- Unauthorized approval denied.
- Resume cannot bypass approval.
- Seeded secret absent from traces/capsules.
- Replay makes no external requests.
- Budgets stop runaway workflows.
- Malicious tool output cannot modify the registry or policy.

Prompt-injection filtering is not itself a security boundary. Enforce permissions and capabilities outside the model.
