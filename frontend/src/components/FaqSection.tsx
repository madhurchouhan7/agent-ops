import React, { useState } from 'react'
import { ChevronDown, CornerDownRight } from 'lucide-react'
import { CornerMarks } from './CornerMarks'

interface FaqItem {
  q: string
  a: string
  category: 'general' | 'runtime' | 'safety'
}

const FAQS: FaqItem[] = [
  {
    category: 'general',
    q: 'What is AgentOps?',
    a: 'AgentOps is a reliable, observable control plane for stateful AI agent workflows. It enforces bounded step budgets, explicit state transitions, persistent monotonic event timelines, code-level policy gates, and human approval reviews.'
  },
  {
    category: 'general',
    q: 'How does AgentOps differ from LangChain, LlamaIndex, or AutoGen?',
    a: 'While orchestration frameworks focus on prompting and LLM abstractions, AgentOps functions as the transactional runtime and governance kernel. We enforce strict database-backed state machines, crash recovery, immutable event history, and approval gates that prevent rogue side-effects.'
  },
  {
    category: 'general',
    q: 'Can I self-host AgentOps locally?',
    a: 'Yes! The entire AgentOps runtime runs locally with a single Python or Docker command. It uses SQLite by default for zero-config local prototyping and seamlessly connects to PostgreSQL for production deployments.'
  },
  {
    category: 'runtime',
    q: 'How does restart recovery work if a worker crashes?',
    a: 'AgentOps persists serializable checkpoints at safe state boundaries along with an immutable monotonic event sequence `(run_id, seq_no)`. When a crashed worker restarts, it restores the state machine from the latest checkpoint and resumes without re-executing already committed side effects.'
  },
  {
    category: 'runtime',
    q: 'What are execution step budgets?',
    a: 'Every workflow is initialized with an explicit maximum step counter (e.g., 15 steps) and wall-clock timeout. If an agent loops repeatedly or exceeds limits, AgentOps halts execution immediately with a BudgetExceededError and marks the run FAILED.'
  },
  {
    category: 'safety',
    q: 'How do code-level Policy Gates protect against bad actions?',
    a: 'Tools in AgentOps are strictly allow-listed and tagged with risk tiers (T0 Safe through T3 Destructive). When an agent attempts an action that mutates external state (like issuing a refund or dropping a database table), the policy gate pauses execution and generates an approval request.'
  },
  {
    category: 'safety',
    q: 'What is a Redacted Failure Capsule?',
    a: 'When an agent run fails or encounters an unhandled exception, AgentOps packages the full execution snapshot into a Failure Capsule. All secrets, auth tokens, customer emails, and PII are redacted so developers can safely download the capsule and reproduce bugs offline without security risks.'
  }
]

export const FaqSection: React.FC = () => {
  const [activeCategory, setActiveCategory] = useState<'all' | 'general' | 'runtime' | 'safety'>('all')
  const [openIndex, setOpenIndex] = useState<number | null>(0)

  const filteredFaqs = activeCategory === 'all' 
    ? FAQS 
    : FAQS.filter(f => f.category === activeCategory)

  return (
    <section id="faq" className="relative py-24 sm:py-32 border-t border-white/[0.08] bg-[#050507]">
      <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8 relative">
        <CornerMarks />

        {/* Section Header */}
        <div className="mx-auto max-w-2xl text-center space-y-4 mb-12">
          <h2 className="text-3xl sm:text-5xl font-bold tracking-tight text-white">
            Frequently asked questions.
          </h2>
          <p className="text-neutral-400 text-base sm:text-lg">
            Quick answers about runtime safety, persistence, and workflow recovery.
          </p>

          {/* Filter categories */}
          <div className="inline-flex items-center gap-2 p-1 rounded-full border border-white/10 bg-neutral-950 mt-4">
            {(['all', 'general', 'runtime', 'safety'] as const).map(cat => (
              <button
                key={cat}
                onClick={() => setActiveCategory(cat)}
                className={`text-xs capitalize font-medium px-3.5 py-1.5 rounded-full transition ${
                  activeCategory === cat
                    ? 'bg-white text-black font-semibold'
                    : 'text-neutral-400 hover:text-white'
                }`}
              >
                {cat === 'all' ? 'All Questions' : cat}
              </button>
            ))}
          </div>
        </div>

        {/* Accordion list */}
        <div className="divide-y divide-white/10 border-y border-white/10">
          {filteredFaqs.map((faq, idx) => {
            const isOpen = openIndex === idx
            return (
              <div key={idx} className="py-6">
                <button
                  onClick={() => setOpenIndex(isOpen ? null : idx)}
                  className="flex w-full items-center justify-between text-left group"
                >
                  <span className="text-base sm:text-lg font-medium text-white group-hover:text-neutral-300 transition">
                    {faq.q}
                  </span>
                  <div className={`size-7 rounded-full border border-white/15 bg-white/5 flex items-center justify-center shrink-0 transition-transform duration-200 ${
                    isOpen ? 'rotate-180 bg-white text-black' : 'text-neutral-400'
                  }`}>
                    <ChevronDown className="size-4" />
                  </div>
                </button>

                {isOpen && (
                  <div className="mt-3 text-sm text-neutral-400 leading-relaxed pl-1 pr-6 animate-fd-fade-in">
                    {faq.a}
                  </div>
                )}
              </div>
            )
          })}
        </div>

      </div>
    </section>
  )
}
