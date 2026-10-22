# Synthesized Context

## Core Problem and Target Users
- source: docs/02-problem-and-solution.md
- content: Agents are brittle in production due to lost in-memory state on crashes, duplicated side-effects on blind retries, unauthorized tool calls, skipped human approvals, and inability to reproduce failures as regression tests. Target users are AI agent developers building tool-using workflows and small engineering teams needing visibility, approvals, and audit trails.

## User Flows and UX Rules
- source: docs/04-user-flows.md
- content: Three primary user journeys: (A) Create and inspect a run with step-by-step state projection and event timeline; (B) Human approval before protected action with reviewer identity and persistent audit trail; (C) Failure diagnosis via timeline inspection, redacted capsule export, and offline mock replay. UX rules mandate clear distinction between trace replay and live execution, separate display of lifecycle status from current node, and explicit presentation of action scope before approval.

## Testing Strategy and Release Gates
- source: docs/12-testing-and-release-gates.md
- content: Release progression: MVP Gate (unit tests pass, demo completes, pause/resume works, restart recovery passes, security tests pass); Portfolio Release Gate (API/DB integration passes, clean-clone setup works, golden trajectories pass in CI); Production Gate (auth/authz audit, backup/restore rehearsal, load and failure tests meet targets).

## Terminology and Glossary
- source: docs/13-glossary.md
- content: Definitions for Agent, Workflow, Run, Node, Lifecycle status, Checkpoint, Event, Trajectory, Tool registry, Policy gate, HITL, Idempotency key, Unknown outcome, Failure Capsule, Mock replay, Golden trajectory, RPO, RTO, ADR.
