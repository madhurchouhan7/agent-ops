import React from 'react'
import { 
  GitFork, 
  ShieldCheck, 
  History, 
  FileLock2, 
  ArrowRight, 
  Terminal, 
  Activity,
  CheckCircle,
  Clock,
  Layers
} from 'lucide-react'
import { CornerMarks } from './CornerMarks'

export const BentoGrid: React.FC = () => {
  return (
    <section id="features" className="relative py-24 sm:py-32 bg-[#050507]">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        
        {/* Section Header */}
        <div className="mx-auto max-w-3xl text-center space-y-4 mb-16">
          <span className="text-xs font-mono uppercase tracking-widest text-neutral-400 bg-white/5 px-3 py-1 rounded-full border border-white/10">
            Core Architecture
          </span>
          <h2 className="text-3xl sm:text-5xl font-bold tracking-tight text-white">
            Everything you need to govern stateful AI agents
          </h2>
          <p className="text-neutral-400 text-base sm:text-lg">
            Built from first principles for reliability. Bounded state machines, persistent monotonic timelines, policy gates, and failure capsules.
          </p>
        </div>

        {/* Bento Grid */}
        <div className="grid grid-cols-1 md:grid-cols-12 gap-6">

          {/* Card 1: State Machine & Bounded Runtime (Span 7) */}
          <div className="md:col-span-7 relative rounded-3xl border border-white/10 bg-black/60 p-6 sm:p-8 overflow-hidden group hover:border-white/20 transition-all">
            <CornerMarks />
            <div className="flex items-center gap-3 mb-4">
              <div className="size-10 rounded-xl bg-white/10 border border-white/20 flex items-center justify-center text-white">
                <GitFork className="size-5" />
              </div>
              <div>
                <h3 className="text-lg font-bold text-white tracking-tight">Explicit State Machine & Budgets</h3>
                <p className="text-xs text-neutral-400 font-mono">Guaranteed valid transitions • Step & wall-clock caps</p>
              </div>
            </div>

            <p className="text-sm text-neutral-300 leading-relaxed mb-6">
              Agent execution is bound by strict state transition matrices. Invalid state hops and modifications from terminal states raise explicit domain errors, preventing rogue agent drift.
            </p>

            {/* Visual State Diagram Widget */}
            <div className="rounded-xl border border-white/10 bg-neutral-950 p-4 font-mono text-xs space-y-3">
              <div className="flex items-center justify-between text-[11px] text-neutral-500 pb-2 border-b border-white/5">
                <span>Domain State Machine Matrix</span>
                <span className="text-emerald-400 flex items-center gap-1">
                  <CheckCircle className="size-3" /> Strict Transition Guard
                </span>
              </div>
              <div className="grid grid-cols-3 sm:grid-cols-5 gap-2 text-center text-[10px]">
                <div className="p-2 rounded bg-white/5 border border-white/10 text-neutral-300">
                  <span className="text-neutral-500 block text-[9px]">INIT</span>
                  CREATED
                </div>
                <div className="p-2 rounded bg-white/15 border border-white/30 text-white font-semibold shadow-sm">
                  <span className="text-cyan-400 block text-[9px]">ACTIVE</span>
                  RUNNING
                </div>
                <div className="p-2 rounded bg-amber-500/10 border border-amber-500/30 text-amber-300">
                  <span className="text-amber-400 block text-[9px]">GATE</span>
                  PAUSED
                </div>
                <div className="p-2 rounded bg-emerald-500/10 border border-emerald-500/30 text-emerald-300">
                  <span className="text-emerald-400 block text-[9px]">TERMINAL</span>
                  SUCCEEDED
                </div>
                <div className="p-2 rounded bg-rose-500/10 border border-rose-500/30 text-rose-300">
                  <span className="text-rose-400 block text-[9px]">TERMINAL</span>
                  FAILED
                </div>
              </div>
              <div className="flex items-center justify-between pt-1 text-[11px] text-neutral-400">
                <span>Budget Enforcement: Max 15 steps</span>
                <span className="text-neutral-300 font-mono">Timeout: 30.0s</span>
              </div>
            </div>
          </div>

          {/* Card 2: Policy Gate & Human Approvals (Span 5) */}
          <div className="md:col-span-5 relative rounded-3xl border border-white/10 bg-black/60 p-6 sm:p-8 overflow-hidden group hover:border-white/20 transition-all">
            <CornerMarks />
            <div className="flex items-center gap-3 mb-4">
              <div className="size-10 rounded-xl bg-white/10 border border-white/20 flex items-center justify-center text-white">
                <ShieldCheck className="size-5" />
              </div>
              <div>
                <h3 className="text-lg font-bold text-white tracking-tight">Code-Enforced Policy Gate</h3>
                <p className="text-xs text-neutral-400 font-mono">T0-T3 Risk Tiers • Human Approvals</p>
              </div>
            </div>

            <p className="text-sm text-neutral-300 leading-relaxed mb-6">
              Protected actions pause execution and persist an approval request. Rejected actions guarantee the tool never runs.
            </p>

            {/* Simulated Approval Gate */}
            <div className="rounded-xl border border-amber-500/20 bg-amber-500/[0.04] p-4 text-xs space-y-2.5">
              <div className="flex items-center justify-between">
                <span className="font-mono font-semibold text-amber-300">Pending Review #appr-901</span>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-amber-500/20 text-amber-200">
                  Tier-2 Protected
                </span>
              </div>
              <p className="text-neutral-300 text-[11px]">
                Tool: <code className="text-white bg-black/40 px-1 py-0.5 rounded">send_reply</code> with parameter: <code className="text-white bg-black/40 px-1 py-0.5 rounded">refund_amount: $149.00</code>
              </p>
              <div className="flex items-center gap-2 pt-1">
                <span className="flex-1 text-center py-1 rounded bg-white text-black font-semibold text-[11px]">
                  Approve (Authorized)
                </span>
                <span className="flex-1 text-center py-1 rounded bg-neutral-900 border border-white/20 text-neutral-300 font-medium text-[11px]">
                  Reject & Abort
                </span>
              </div>
            </div>
          </div>

          {/* Card 3: Deterministic Offline Mock Replay (Span 5) */}
          <div className="md:col-span-5 relative rounded-3xl border border-white/10 bg-black/60 p-6 sm:p-8 overflow-hidden group hover:border-white/20 transition-all">
            <CornerMarks />
            <div className="flex items-center gap-3 mb-4">
              <div className="size-10 rounded-xl bg-white/10 border border-white/20 flex items-center justify-center text-white">
                <History className="size-5" />
              </div>
              <div>
                <h3 className="text-lg font-bold text-white tracking-tight">Offline Mock Replay</h3>
                <p className="text-xs text-neutral-400 font-mono">Zero network side-effects • CI Verification</p>
              </div>
            </div>

            <p className="text-sm text-neutral-300 leading-relaxed mb-4">
              Recorded trajectories replay deterministically using recorded tool outputs without pinging third-party APIs or sending real emails.
            </p>

            <div className="rounded-xl border border-white/10 bg-neutral-950 p-3 font-mono text-[11px] text-neutral-400 space-y-1.5">
              <div className="flex items-center justify-between text-neutral-500">
                <span>Golden Trajectory Evaluator</span>
                <span className="text-white">CI Test Pass</span>
              </div>
              <div className="text-neutral-300">
                &gt; pytest tests/trajectories/ -v<br />
                <span className="text-emerald-400">PASSED:</span> test_support_triage_golden<br />
                <span className="text-emerald-400">PASSED:</span> test_policy_rejection_safety
              </div>
            </div>
          </div>

          {/* Card 4: Redacted Failure Capsules & Checkpoint Recovery (Span 7) */}
          <div className="md:col-span-7 relative rounded-3xl border border-white/10 bg-black/60 p-6 sm:p-8 overflow-hidden group hover:border-white/20 transition-all">
            <CornerMarks />
            <div className="flex items-center gap-3 mb-4">
              <div className="size-10 rounded-xl bg-white/10 border border-white/20 flex items-center justify-center text-white">
                <FileLock2 className="size-5" />
              </div>
              <div>
                <h3 className="text-lg font-bold text-white tracking-tight">Redacted Failure Capsules & Recovery</h3>
                <p className="text-xs text-neutral-400 font-mono">Automated PII scrubbing • Resumption from Checkpoints</p>
              </div>
            </div>

            <p className="text-sm text-neutral-300 leading-relaxed mb-6">
              When a workflow fails, AgentOps exports a self-contained diagnostic capsule with credentials and personal data completely sanitized. Survives process crashes and restarts cleanly.
            </p>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs font-mono">
              <div className="p-3 rounded-xl border border-white/10 bg-neutral-950 space-y-1">
                <span className="text-neutral-500 block text-[10px] uppercase">Automated Redaction</span>
                <span className="text-white block font-semibold">Zero Secrets Leakage</span>
                <p className="text-neutral-400 text-[10px] font-sans">Emails, tokens, and Authorization headers masked as [REDACTED_SECRET].</p>
              </div>
              <div className="p-3 rounded-xl border border-white/10 bg-neutral-950 space-y-1">
                <span className="text-neutral-500 block text-[10px] uppercase">Durable Checkpoints</span>
                <span className="text-white block font-semibold">PostgreSQL & SQLite</span>
                <p className="text-neutral-400 text-[10px] font-sans">Monotonic sequence numbering (run_id, seq_no) with restart recovery.</p>
              </div>
            </div>
          </div>

        </div>
      </div>
    </section>
  )
}
