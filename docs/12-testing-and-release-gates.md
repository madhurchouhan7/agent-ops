# Testing and Release Gates

## Unit tests
Transitions, terminal states, retry caps, budgets, pause/resume/cancel, serialization, checkpoint validation, tool schemas, policy, redaction, event ordering.

## Integration tests
Runtime + DB; API + PostgreSQL; approval across restart; idempotent run creation; duplicate approval; concurrent updates; clean migration; capsule export.

## Fault injection
Crash before tool call; crash after tool call before result persistence; event/checkpoint ordering crash; DB outage; tool timeout; invalid model output; corrupt checkpoint; duplicate approval request.

## Golden trajectories
Happy path; transient failure recovery; permanent failure; approval approved/rejected; restart recovery; unauthorized tool denied; secret redacted; replay makes no external calls.

## Release gates

### MVP
- [ ] Unit tests pass.
- [ ] Demo completes.
- [ ] Pause/resume and bounded retries work.
- [ ] Checkpoint restore test passes.
- [ ] Critical security tests pass.

### Portfolio release
- [ ] API/database integration tests pass.
- [ ] Frontend build and end-to-end demo pass.
- [ ] Golden trajectory suite runs in CI.
- [ ] Capsule redaction is verified.
- [ ] Clean-clone setup is documented.
- [ ] Limitations are disclosed.

### Production-oriented deployment
- [ ] Authentication/authorization reviewed.
- [ ] Tenant isolation tested if multi-user.
- [ ] Resource budgets configured.
- [ ] Logs/traces contain no secrets.
- [ ] Backup and restore rehearsal completed.
- [ ] Load and failure tests meet documented targets.
- [ ] Runbooks and rollback tested.
- [ ] Security findings triaged.
- [ ] Retention/deletion implemented.
- [ ] Claims have evidence.

## Benchmark template
Commit SHA; environment; workflow/model version; test set size; success definition; policy-violation definition; p50/p95 latency; recovery success; failure categories; cost method; limitations.
