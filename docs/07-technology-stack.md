# Technology Stack and Role

| Technology | Role | Why | Phase |
|---|---|---|---|
| Python 3.11+ | Runtime/backend | Typing, ecosystem, testability | First |
| Pydantic | Validate state, events, tool/API schemas | Strict contracts | Runtime |
| pytest | Unit/integration/trajectory tests | Repeatable checks | First |
| FastAPI | REST control API | Typed endpoints and OpenAPI | API |
| PostgreSQL | Durable run/event/checkpoint data | Transactions and constraints | Persistence |
| SQLAlchemy | DB access | Repository/ORM layer | Persistence |
| Alembic | Migrations | Repeatable schema evolution | Persistence |
| Next.js + TypeScript | Web console | Developer-facing UI | UI |
| React Flow | Optional graph visualization | Visual workflow view | Later |
| Docker Compose | Local services | Reproducible setup | Integration |
| GitHub Actions | CI | Enforce checks | Early |
| OpenTelemetry | Traces/metrics | Cross-component observability | Hardening |
| Redis | Optional queue/cache | Dispatch/backpressure if needed | Later |
| Playwright | Browser end-to-end tests | UI verification | UI |
| LangGraph / Temporal | Optional framework/backend comparison | Durability trade-offs | After core |

## Principles
Start with few dependencies. Pin versions when implementation begins. Do not add Redis, a vector DB, Kubernetes, or a model API merely to make the stack look impressive. Use mocked model outputs for deterministic tests. Keep secrets out of source control. Document actual versions and commands.
