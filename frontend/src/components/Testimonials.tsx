import React from 'react'
import { CornerMarks } from './CornerMarks'

const TESTIMONIALS = [
  {
    quote: "AgentOps eliminated our greatest anxiety with autonomous agents — runaway loops and unapproved destructive actions. The policy gate and human-in-the-loop review saved us from accidental database drops.",
    author: "Elena Rostova",
    role: "VP of Engineering · CloudMatrix"
  },
  {
    quote: "Deterministic offline mock replay means our CI test suites run in 4 seconds with zero network calls to LLMs, yet test 100% of the agent trajectory state transitions.",
    author: "Marcus Chen",
    role: "AI Platform Lead · Helix Systems"
  },
  {
    quote: "The failure capsules are unbelievable. When an agent errors out in staging, we download one zip file with all PII sanitized and reproduce the exact bug offline in minutes.",
    author: "Sarah Mitchell",
    role: "Head of Infrastructure · TechScale"
  },
  {
    quote: "Restart recovery saved our financial reconciliation agent when our Kubernetes node OOMed. It booted up, loaded the checkpoint, and resumed sequence #8 without double-charging a single customer.",
    author: "David Vance",
    role: "Chief Architect · Basepoint Capital"
  }
]

export const Testimonials: React.FC = () => {
  return (
    <section className="relative py-24 border-t border-white/[0.08] bg-[#050507] overflow-hidden">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 relative">
        <CornerMarks />

        <div className="mx-auto max-w-3xl text-center space-y-4 mb-16">
          <h2 className="text-3xl sm:text-4xl font-bold tracking-tight text-white">
            Hear from teams building resilient AI agents
          </h2>
          <p className="text-neutral-400 text-base">
            Engineers and platform leaders trust AgentOps to govern, monitor, and recover stateful AI workflows.
          </p>
        </div>

        {/* Testimonials Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {TESTIMONIALS.map((t, idx) => (
            <div 
              key={idx}
              className="rounded-2xl border border-white/10 bg-black/60 p-6 sm:p-8 flex flex-col justify-between hover:border-white/20 transition-all backdrop-blur-sm"
            >
              <p className="text-sm sm:text-base text-neutral-300 leading-relaxed italic mb-6">
                "{t.quote}"
              </p>
              <div className="flex items-center gap-3 pt-4 border-t border-white/5">
                <div className="size-9 rounded-full bg-neutral-800 border border-white/20 flex items-center justify-center font-bold text-xs text-white">
                  {t.author.charAt(0)}
                </div>
                <div>
                  <h4 className="text-sm font-semibold text-white">{t.author}</h4>
                  <p className="text-xs text-neutral-500 font-mono">{t.role}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
