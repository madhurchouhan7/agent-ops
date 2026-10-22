import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  ShieldAlert, 
  CheckCircle2, 
  PauseCircle, 
  RotateCcw, 
  Clock, 
  AlertTriangle, 
  UserCheck, 
  Database, 
  Bot, 
  GitPullRequest, 
  ArrowRight,
  Terminal,
  ChevronRight
} from 'lucide-react'

interface WorkflowPersona {
  id: string
  name: string
  role: string
  badge: string
  badgeVariant: 'warning' | 'error' | 'success' | 'info'
  status: string
  summary: string
  actionRequired?: string
  lastUpdated: string
  currentStep: string
  stepProgress: string
  steps: {
    title: string
    detail: string
    time: string
    status: 'completed' | 'active' | 'pending'
    risk?: string
  }[]
  metadata: {
    runId: string
    runtimeBudget: string
    checkpointsSaved: number
    policyTier: string
  }
}

const PERSONAS: WorkflowPersona[] = [
  {
    id: 'triage',
    name: 'Autonomous Support Triage',
    role: 'Financial & Billing Escalation Agent',
    badge: 'PAUSED: Human Approval',
    badgeVariant: 'warning',
    status: 'PAUSED',
    summary: 'Customer ticket #4819 requested a duplicate billing refund of $149.00. The agent verified the charge and drafted a refund notification, but paused execution before invoking the protected external tool.',
    actionRequired: 'Human authorization required to invoke send_refund_reply ($149.00 charge reversal)',
    lastUpdated: '12 seconds ago',
    currentStep: 'Step 4 of 5: Protected Action Gate',
    stepProgress: '80%',
    steps: [
      { title: 'classify_ticket', detail: 'Classified intent as billing_refund (confidence: 0.98)', time: '0.4s ago', status: 'completed' },
      { title: 'lookup_ticket', detail: 'Retrieved Stripe invoice in_9381283 and verified duplicate transaction', time: '0.2s ago', status: 'completed' },
      { title: 'draft_response', detail: 'Generated apology and refund confirmation letter with payload summary', time: '0.1s ago', status: 'completed' },
      { title: 'send_refund_reply', detail: 'Protected action paused. Tier-2 approval token generated.', time: 'now', status: 'active', risk: 'Tier-2 Financial' },
    ],
    metadata: {
      runId: 'run-triage-4819-bf9',
      runtimeBudget: '4 / 15 steps (27% budget)',
      checkpointsSaved: 3,
      policyTier: 'T2 Protected Action',
    }
  },
  {
    id: 'migration',
    name: 'Database Schema Migration',
    role: 'Infrastructure Maintenance Agent',
    badge: 'BLOCKED: Policy Gate',
    badgeVariant: 'error',
    status: 'FAILED',
    summary: 'The agent attempted to execute an unvalidated DDL statement dropping a column without prior WAL snapshot verification. The code-enforced Policy Gate failed closed without executing the command.',
    actionRequired: 'Policy Gate prevented destructive DROP statement. Failure Capsule generated.',
    lastUpdated: '2 minutes ago',
    currentStep: 'Step 2 of 10: Policy Gate Rejection',
    stepProgress: '20%',
    steps: [
      { title: 'analyze_schema', detail: 'Inspected 42 tables and detected deprecated schema indexes', time: '2m ago', status: 'completed' },
      { title: 'execute_ddl', detail: 'BLOCKED: DROP COLUMN without backup snapshot disallowed by policy', time: '2m ago', status: 'active', risk: 'Tier-3 Destructive' },
      { title: 'export_failure_capsule', detail: 'PII redacted, environment dumped to capsule_mig_02.zip', time: '2m ago', status: 'completed' },
    ],
    metadata: {
      runId: 'run-mig-8831-c01',
      runtimeBudget: '2 / 20 steps (10% budget)',
      checkpointsSaved: 1,
      policyTier: 'T3 Zero-Tolerance',
    }
  },
  {
    id: 'review',
    name: 'Deterministic Code Reviewer',
    role: 'Autonomous PR Safety Agent',
    badge: 'SUCCEEDED: Verified',
    badgeVariant: 'success',
    status: 'SUCCEEDED',
    summary: 'Executed complete verification of PR #214: ran linting, static security analysis, unit test suites with 100% path coverage, and posted a verified trajectory artifact to the pull request.',
    lastUpdated: '14 minutes ago',
    currentStep: 'Step 6 of 6: Completed',
    stepProgress: '100%',
    steps: [
      { title: 'checkout_branch', detail: 'Cloned sha-7e9b4 with strict commit signature verification', time: '15m ago', status: 'completed' },
      { title: 'run_security_scan', detail: '0 vulnerabilities, 0 hardcoded credentials found', time: '14m ago', status: 'completed' },
      { title: 'execute_test_suite', detail: '138 tests passed in 1.4s with synthetic DB harness', time: '14m ago', status: 'completed' },
      { title: 'post_pr_evaluation', detail: 'Monotonic event trace attached to PR review thread', time: '14m ago', status: 'completed' },
    ],
    metadata: {
      runId: 'run-rev-5912-ee7',
      runtimeBudget: '6 / 10 steps (60% budget)',
      checkpointsSaved: 6,
      policyTier: 'T1 Standard Audit',
    }
  },
  {
    id: 'recovery',
    name: 'Incident Recovery Agent',
    role: 'Durable State Resumption Agent',
    badge: 'RESTORED: Checkpoint #4',
    badgeVariant: 'info',
    status: 'RUNNING',
    summary: 'Worker node was abruptly terminated by an OOM event during monotonic sequence #7. Upon restart, AgentOps reconstructed the state machine from Checkpoint #4 and resumed cleanly without replay side-effects.',
    actionRequired: 'Resumed autonomously with zero lost events or duplicate database writes.',
    lastUpdated: 'Just now',
    currentStep: 'Step 8 of 12: In Execution',
    stepProgress: '67%',
    steps: [
      { title: 'process_restart', detail: 'Worker restarted on node ip-10-0-4-12 after abrupt SIGKILL', time: '10s ago', status: 'completed' },
      { title: 'load_checkpoint', detail: 'Queried PostgreSQL store and restored snapshot seq #7', time: '8s ago', status: 'completed' },
      { title: 'reconcile_state', detail: 'Restored step budget (7/12) and resumed active state machine', time: '5s ago', status: 'completed' },
      { title: 'continue_workflow', detail: 'Executing next node in sequence with fresh event id', time: 'now', status: 'active' },
    ],
    metadata: {
      runId: 'run-rec-1029-a41',
      runtimeBudget: '8 / 12 steps (67% budget)',
      checkpointsSaved: 4,
      policyTier: 'T0 Recovery Guard',
    }
  }
]

export const HeroWorkflowSwitcher: React.FC = () => {
  const [selectedId, setSelectedId] = useState('triage')
  const current = PERSONAS.find(p => p.id === selectedId) || PERSONAS[0]

  return (
    <div className="w-full max-w-5xl mx-auto rounded-2xl border border-white/10 bg-[#08080a] p-4 sm:p-6 shadow-2xl backdrop-blur-xl relative overflow-hidden">
      {/* Background radial highlight */}
      <div className="absolute -top-32 -right-32 size-96 rounded-full bg-white/[0.03] blur-3xl pointer-events-none" />

      {/* Tabs / Switcher Bar */}
      <div className="flex flex-wrap items-center gap-2 border-b border-white/10 pb-4 mb-6">
        <span className="text-xs font-mono uppercase text-neutral-500 mr-2 flex items-center gap-1.5">
          <Bot className="size-3.5 text-neutral-400" />
          Live Agent Trajectories:
        </span>
        {PERSONAS.map(p => {
          const isActive = p.id === selectedId
          return (
            <button
              key={p.id}
              onClick={() => setSelectedId(p.id)}
              className={`text-xs font-medium px-3 py-1.5 rounded-full transition-all flex items-center gap-2 ${
                isActive
                  ? 'bg-white text-black font-semibold shadow-md'
                  : 'bg-white/5 text-neutral-400 hover:text-white hover:bg-white/10 border border-white/5'
              }`}
            >
              <span className={`size-1.5 rounded-full ${
                p.badgeVariant === 'warning' ? 'bg-amber-400' :
                p.badgeVariant === 'error' ? 'bg-rose-500' :
                p.badgeVariant === 'success' ? 'bg-emerald-400' : 'bg-cyan-400'
              }`} />
              {p.name}
            </button>
          )
        })}
      </div>

      {/* Card Content Area */}
      <AnimatePresence mode="wait">
        <motion.div
          key={current.id}
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -8 }}
          transition={{ duration: 0.2 }}
          className="grid grid-cols-1 lg:grid-cols-12 gap-6"
        >
          {/* Left Column: Workflow Details */}
          <div className="lg:col-span-7 flex flex-col justify-between space-y-6">
            <div>
              {/* Header with Title and Status Badge */}
              <div className="flex flex-wrap items-center justify-between gap-3 mb-2">
                <div>
                  <h3 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
                    {current.name}
                  </h3>
                  <p className="text-xs text-neutral-400 font-mono mt-0.5">{current.role}</p>
                </div>
                <span className={`inline-flex items-center gap-1.5 text-xs font-mono px-2.5 py-1 rounded-full border ${
                  current.badgeVariant === 'warning'
                    ? 'border-amber-500/30 bg-amber-500/10 text-amber-300'
                    : current.badgeVariant === 'error'
                    ? 'border-rose-500/30 bg-rose-500/10 text-rose-300'
                    : current.badgeVariant === 'success'
                    ? 'border-emerald-500/30 bg-emerald-500/10 text-emerald-300'
                    : 'border-cyan-500/30 bg-cyan-500/10 text-cyan-300'
                }`}>
                  {current.badgeVariant === 'warning' && <PauseCircle className="size-3.5" />}
                  {current.badgeVariant === 'error' && <AlertTriangle className="size-3.5" />}
                  {current.badgeVariant === 'success' && <CheckCircle2 className="size-3.5" />}
                  {current.badgeVariant === 'info' && <RotateCcw className="size-3.5" />}
                  {current.badge}
                </span>
              </div>

              {/* Summary Description */}
              <p className="text-sm text-neutral-300 leading-relaxed mt-4 bg-white/[0.02] p-3.5 rounded-lg border border-white/5">
                {current.summary}
              </p>

              {/* Action Alert Callout if present */}
              {current.actionRequired && (
                <div className="mt-4 flex items-start gap-3 p-3 rounded-lg border border-amber-500/20 bg-amber-500/5 text-amber-200 text-xs">
                  <UserCheck className="size-4 shrink-0 text-amber-400 mt-0.5" />
                  <div>
                    <span className="font-semibold block text-amber-300">Human-in-the-Loop Gate Active</span>
                    <span className="text-neutral-300">{current.actionRequired}</span>
                  </div>
                </div>
              )}
            </div>

            {/* Run Metadata Grid */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-4 border-t border-white/10 text-xs font-mono">
              <div className="bg-white/[0.03] p-2.5 rounded-md border border-white/5">
                <span className="text-neutral-500 block text-[10px] uppercase">Run Identifier</span>
                <span className="text-neutral-200 truncate block mt-0.5">{current.metadata.runId}</span>
              </div>
              <div className="bg-white/[0.03] p-2.5 rounded-md border border-white/5">
                <span className="text-neutral-500 block text-[10px] uppercase">Step Budget</span>
                <span className="text-neutral-200 block mt-0.5">{current.metadata.runtimeBudget}</span>
              </div>
              <div className="bg-white/[0.03] p-2.5 rounded-md border border-white/5">
                <span className="text-neutral-500 block text-[10px] uppercase">Checkpoints</span>
                <span className="text-neutral-200 block mt-0.5">{current.metadata.checkpointsSaved} saved</span>
              </div>
              <div className="bg-white/[0.03] p-2.5 rounded-md border border-white/5">
                <span className="text-neutral-500 block text-[10px] uppercase">Safety Tier</span>
                <span className="text-neutral-200 block mt-0.5">{current.metadata.policyTier}</span>
              </div>
            </div>
          </div>

          {/* Right Column: Execution Timeline Trace */}
          <div className="lg:col-span-5 bg-black/60 rounded-xl p-4 border border-white/10 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between pb-3 border-b border-white/10">
                <span className="text-xs font-mono text-neutral-400 flex items-center gap-1.5">
                  <Clock className="size-3.5 text-neutral-500" />
                  Monotonic Event Timeline
                </span>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-white/10 text-neutral-300">
                  {current.stepProgress}
                </span>
              </div>

              {/* Timeline Steps */}
              <div className="mt-4 space-y-3">
                {current.steps.map((step, idx) => (
                  <div key={idx} className="relative flex items-start gap-3 text-xs">
                    {/* Step line connector */}
                    {idx < current.steps.length - 1 && (
                      <span className="absolute left-[9px] top-4 w-[1px] h-full bg-white/10" />
                    )}

                    {/* Step node icon */}
                    <div className={`size-5 rounded-full flex items-center justify-center shrink-0 z-10 ${
                      step.status === 'completed'
                        ? 'bg-neutral-800 text-white border border-white/30'
                        : step.status === 'active'
                        ? 'bg-white text-black font-bold ring-2 ring-white/30'
                        : 'bg-neutral-900 text-neutral-500 border border-white/10'
                    }`}>
                      {step.status === 'completed' ? (
                        <CheckCircle2 className="size-3 text-white" />
                      ) : (
                        <span className="text-[10px]">{idx + 1}</span>
                      )}
                    </div>

                    {/* Step content */}
                    <div className="flex-1 pb-1">
                      <div className="flex items-center justify-between">
                        <span className="font-mono font-medium text-white">{step.title}</span>
                        <span className="text-[10px] font-mono text-neutral-500">{step.time}</span>
                      </div>
                      <p className="text-neutral-400 text-[11px] mt-0.5 leading-snug">{step.detail}</p>
                      {step.risk && (
                        <span className="inline-block mt-1 text-[9px] font-mono px-1.5 py-0.5 rounded border border-amber-500/30 text-amber-300 bg-amber-500/10">
                          {step.risk}
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Bottom status line */}
            <div className="pt-3 mt-3 border-t border-white/5 flex items-center justify-between text-[11px] text-neutral-500 font-mono">
              <span>Last active: {current.lastUpdated}</span>
              <span className="text-neutral-400 hover:text-white transition cursor-pointer flex items-center gap-1">
                Inspect Raw Timeline <ChevronRight className="size-3" />
              </span>
            </div>
          </div>
        </motion.div>
      </AnimatePresence>
    </div>
  )
}
