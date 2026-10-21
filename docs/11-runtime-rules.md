# Runtime Rules and Invariants

These rules are normative for V1. Changes must update tests and relevant docs.

## State
1. Each run has one lifecycle status and one current node.
2. Every transition is validated against the workflow definition.
3. `SUCCEEDED`, `FAILED`, and `CANCELLED` are terminal.
4. `PAUSED` cannot advance until a valid resume/approval event.
5. Terminal runs cannot resume.
6. Cancellation stops future steps; in-flight semantics are documented.
7. Every run has max-step and wall-clock budgets.
8. Retries are bounded.

## Tools
9. Model output cannot invoke arbitrary functions/imports.
10. Tools must be registered and schema-validated.
11. Policy checks happen before execution.
12. Unknown/unauthorized tools fail closed.
13. Tool output is untrusted and validated before entering state.
14. Timeouts and output limits are mandatory.
15. Permission and validation errors are not automatically retried.
16. Retry transient failures only if repeat is safe.
17. Uncertain side effects become `UNKNOWN_OUTCOME` and are reconciled before retry.

## Persistence
18. Event sequence is monotonic per run.
19. Event history is append-oriented.
20. Checkpoints are versioned and validated.
21. Persist only serializable, approved state fields.
22. Never store credentials in state, events, logs, or capsules.
23. Test ordering and crash windows for action, event, and checkpoint writes.

## Approval and replay
24. Approval is tied to a specific run/action.
25. Only authorized users can decide.
26. Duplicate/expired decisions follow a documented idempotency contract.
27. Rejection never executes the protected action.
28. Decisions are recorded in history.
29. Replay is read-only/mock-only by default.
30. Recorded outputs never trigger external actions.
31. Capsules are versioned and redacted.
32. Critical trajectory assertions run in CI.
33. Final text alone does not prove a safe successful run.

## Error categories
`VALIDATION_ERROR`, `POLICY_DENIED`, `TRANSIENT_TOOL_ERROR`, `TOOL_TIMEOUT`, `MODEL_OUTPUT_INVALID`, `PERSISTENCE_ERROR`, `UNKNOWN_OUTCOME`, `BUDGET_EXCEEDED`, `INVALID_TRANSITION`.
