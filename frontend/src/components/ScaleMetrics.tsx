import React, { useState } from 'react'
import { CornerMarks } from './CornerMarks'
import { Activity, ShieldCheck, Zap, Database, ArrowRight } from 'lucide-react'

const TABS = [
  {
    id: 'triage',
    title: 'Customer Support & Triage',
    description: 'Autonomous ticket parsing, customer lookup, and reply drafting with human review on refunds and SLA credits.',
    stat: '94% faster triage resolution',
    example: 'Drafts responses and pauses for manager approval when refund amount exceeds $50.'
  },
  {
    id: 'infra',
    title: 'Infrastructure & DB Operations',
    description: 'Safe database maintenance agents with code-level policy enforcement preventing destructive DDL commands.',
    stat: '0 accidental schema drops',
    example: 'Disallows DROP TABLE/COLUMN without active snapshot verification.'
  },
  {
    id: 'security',
    title: 'Security & Code Review CI/CD',
    description: 'Deterministic trajectory evaluation running in CI pipelines verifying state transitions and tool permissions.',
    stat: '100% trajectory reproducibility',
    example: 'Replays offline mock events in GitHub Actions with zero network calls.'
  },
  {
    id: 'finance',
    title: 'Financial Operations & Billing',
    description: 'High-stakes multi-step reconciliation with persistent monotonic timelines and immutable audit logs.',
    stat: '100% monotonic event audit trail',
    example: 'Maintains tamper-proof event sequences with restart resumption.'
  }
]

export const ScaleMetrics: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0)

  return (
    <section id="scale" className="relative py-24 border-t border-white/[0.08] bg-black overflow-hidden">
      {/* Background SVG wave pattern */}
      <svg 
        aria-hidden="true" 
        viewBox="0 0 1400 600" 
        className="pointer-events-none absolute inset-0 size-full opacity-10 stroke-white fill-none"
      >
        <path d="M0,100 C300,300 600,0 900,200 C1200,400 1300,100 1400,250" strokeWidth="1.5" strokeDasharray="4 4" />
        <path d="M0,250 C400,100 700,400 1000,150 C1250,50 1350,300 1400,350" strokeWidth="1" />
        <path d="M0,450 C350,350 800,550 1100,300 C1250,150 1350,500 1400,450" strokeWidth="1.5" strokeDasharray="6 6" />
      </svg>

      <div className="relative mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <CornerMarks />

        {/* Section Header */}
        <div className="mx-auto max-w-3xl text-center space-y-4 mb-16">
          <h2 className="text-3xl sm:text-5xl font-bold tracking-tight text-white">
            Built for the scale of agentic execution
          </h2>
          <p className="text-neutral-400 text-base sm:text-lg">
            AgentOps handles millions of state transitions with sub-millisecond event sequencing and zero-loss crash recovery.
          </p>
        </div>

        {/* 4 Big Metrics Grid */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-6 mb-16">
          <div className="rounded-2xl border border-white/10 bg-neutral-950/60 p-6 text-center backdrop-blur-sm">
            <span className="text-3xl sm:text-5xl font-extrabold text-white font-mono tracking-tight block">
              850M+
            </span>
            <span className="text-xs uppercase font-mono tracking-wider text-neutral-400 mt-2 block">
              State Transitions Executed
            </span>
          </div>

          <div className="rounded-2xl border border-white/10 bg-neutral-950/60 p-6 text-center backdrop-blur-sm">
            <span className="text-3xl sm:text-5xl font-extrabold text-white font-mono tracking-tight block">
              &lt; 5ms
            </span>
            <span className="text-xs uppercase font-mono tracking-wider text-neutral-400 mt-2 block">
              Monotonic Event Latency
            </span>
          </div>

          <div className="rounded-2xl border border-white/10 bg-neutral-950/60 p-6 text-center backdrop-blur-sm">
            <span className="text-3xl sm:text-5xl font-extrabold text-white font-mono tracking-tight block">
              99.99%
            </span>
            <span className="text-xs uppercase font-mono tracking-wider text-neutral-400 mt-2 block">
              Restart Recovery Guarantee
            </span>
          </div>

          <div className="rounded-2xl border border-white/10 bg-neutral-950/60 p-6 text-center backdrop-blur-sm">
            <span className="text-3xl sm:text-5xl font-extrabold text-white font-mono tracking-tight block">
              100%
            </span>
            <span className="text-xs uppercase font-mono tracking-wider text-neutral-400 mt-2 block">
              Policy Gate Enforcement
            </span>
          </div>
        </div>

        {/* Category Tabs Section */}
        <div className="rounded-2xl border border-white/10 bg-[#09090b] p-6 sm:p-8">
          <div className="flex flex-wrap items-center gap-2 border-b border-white/10 pb-4 mb-6">
            {TABS.map((tab, idx) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(idx)}
                className={`text-xs sm:text-sm font-medium px-4 py-2 rounded-full transition ${
                  activeTab === idx
                    ? 'bg-white text-black font-semibold'
                    : 'text-neutral-400 hover:text-white bg-white/5'
                }`}
              >
                {tab.title}
              </button>
            ))}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-12 gap-6 items-center">
            <div className="md:col-span-8 space-y-3">
              <h3 className="text-xl font-bold text-white">{TABS[activeTab].title}</h3>
              <p className="text-sm text-neutral-300 leading-relaxed">{TABS[activeTab].description}</p>
              <div className="pt-2">
                <span className="inline-block text-xs font-mono px-3 py-1 rounded bg-white/10 border border-white/15 text-neutral-200">
                  Example: {TABS[activeTab].example}
                </span>
              </div>
            </div>

            <div className="md:col-span-4 rounded-xl border border-white/10 bg-black/60 p-5 text-center">
              <span className="text-xs uppercase font-mono text-neutral-500 block mb-1">Impact Metric</span>
              <span className="text-lg font-bold text-white block">{TABS[activeTab].stat}</span>
            </div>
          </div>
        </div>

      </div>
    </section>
  )
}
