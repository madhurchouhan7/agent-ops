# Phase 6: Modern Frontend Redesign & Vertex Landing Page — Research

**Phase:** 06  
**Status:** In-Progress  
**Date:** 2026-10-22  
**Target:** High-fidelity Vertex-inspired monochrome landing page and modern React control console with Framer Motion animations

## User Constraints & Core Requirements

### Locked Decisions
- **Design Inspiration**: `https://vertex-one-lovat.vercel.app/` — Ruixen UI Vertex design system.
- **Visual Aesthetic**: Pure black & white / monochrome minimal dark mode (`#000000`, `#09090b`, `#18181b`, `#27272a`, `#ffffff`, `#a1a1aa`).
- **Animations**: Fluid, subtle, high-performance interactions using Framer Motion and Tailwind CSS transitions.
- **Frontend Stack**: React 18/19 + Vite + Tailwind CSS + Lucide React + Framer Motion.
- **Integration**:
  - Frontend lives in `frontend/` directory with `package.json` and build scripts.
  - Builds into `src/agent_ops/api/static/` so FastAPI serves the complete bundle with no extra reverse-proxy needed in production.
  - Development mode (`npm run dev`) proxies `/v1` requests to FastAPI on `http://localhost:8000`.

## Design System Breakdown (from Vertex One analysis)

### 1. Typography & Grid
- **Font Stack**: Geist / Geist Mono with fallback to system sans/mono.
- **Header Styles**: Tracking tight/tighter (`-0.03em`), bold headings (`text-4xl` to `text-6xl`).
- **Corner Marks**: Characteristic `+` crosshair marks at container corners using absolute pseudo-elements / spans.
- **Borders**: Subtle dashed or 1px border `border-neutral-800` / `border-white/10`.

### 2. Core Sections from Vertex
1. **Fixed Navigation Bar**:
   - Blurred backdrop (`backdrop-blur-md bg-black/60`).
   - AgentOps monochrome logo + brand name.
   - Links: Features, Architecture, Approvals, Pricing, Docs.
   - Primary CTA: "Launch Console" / "Start Demo".
2. **Hero Section**:
   - Pill badge with sparkle: `✨ AI-Native Agent Observability & Governance`.
   - Title: `Automate and govern stateful AI agents`.
   - Subtitle: `Strict state machines, monotonic timelines, policy-enforced human gates, failure capsules, and offline replay.`
   - CTAs: "Launch Live Console", "Read Documentation", "Start Free Run".
   - **Interactive Workflow Run Switcher Card**:
     - Modeled directly on Vertex's customer persona switcher (Devon Park, Marcus Chen, etc.).
     - 4 tabs representing realistic AI Agent workflows:
       1. *Support Triage Agent* (PAUSED at Human Approval: Refund $149)
       2. *Database Migration Agent* (BLOCKED by T2 Policy Gate)
       3. *Code Review & PR Agent* (SUCCEEDED, 14 monotonic events)
       4. *Incident Recovery Agent* (RESTORED from versioned checkpoint #4)
     - Interactive switcher displaying detailed step events, tool parameters, risk tiers, and live status badges.
3. **Logo / Tech Stack Marquee**:
   - Continuous animated infinite scroll featuring Anthropic, OpenAI, Supabase, Linear, GitHub, Slack, Notion, Python, FastAPI, Docker, PostgreSQL.
4. **Bento Grid (Core Capabilities)**:
   - Card 1: *State Machine & Transition Guard* (visual state graph with CREATED -> RUNNING -> PAUSED -> SUCCEEDED).
   - Card 2: *Policy Gate & Human Approvals* (interactive simulation of human approval gate).
   - Card 3: *Deterministic Offline Mock Replay* (zero-network trajectory reproduction).
   - Card 4: *Redacted Failure Capsules* (automatic PII scrubbing & diagnostics export).
5. **Scale & Infrastructure Metrics**:
   - SVG background with subtle wave lines.
   - 4 metrics: 850M+ Step transitions, 99.99% Recovery rate, <5ms Event latency, 100% Policy enforcement.
   - Interactive category tabs.
6. **Social Proof / Testimonials**:
   - Marquee of testimonials from AI platform engineers and engineering leads.
7. **Pricing Table**:
   - Monthly / Annual toggle with savings badge.
   - Community ($0), Team ($29/mo), Enterprise (Custom).
8. **Interactive FAQ**:
   - Categories (General, Runtime & Safety, Integrations & API).
   - Smooth accordion collapse/expand.
9. **Final CTA Banner**:
   - Concentric glowing circular rings (matching Vertex's signature 800px circular disc).
   - "Connect your stack and govern agents today."
10. **Footer**:
    - Product, Solutions, Resources, Company columns.
    - System operational badge (`● All Systems Operational`).

### 3. Redesigned Live Web Console
- Direct toggle from the navbar ("Launch Console" / "Return to Landing Page").
- Full feature parity with existing FastAPI endpoints:
  - Submit Support Ticket & Start Demo (`POST /v1/demo/triage/start`).
  - Pending Approvals Drawer / Modal with Approve and Reject actions (`POST /v1/approvals/{id}/decide`).
  - Resume Run (`POST /v1/demo/triage/{run_id}/resume`).
  - Live Run Cards with status pill (`RUNNING`, `PAUSED`, `SUCCEEDED`, `FAILED`).
  - Step counter & wall-clock budget progress bars.
  - Monotonic Event Stream timeline with sequence badges, timestamps, and expandable payload JSON.
  - Redacted Failure Capsule viewer and JSON/zip downloader.
  - Trajectory Evaluation runner with pass/fail breakdown (`POST /v1/evaluations/run`).
