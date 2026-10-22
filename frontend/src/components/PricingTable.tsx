import React, { useState } from 'react'
import { Check, ArrowRight } from 'lucide-react'
import { CornerMarks } from './CornerMarks'

interface PricingTableProps {
  onSelectPlan?: (plan: string) => void
}

export const PricingTable: React.FC<PricingTableProps> = ({ onSelectPlan }) => {
  const [annual, setAnnual] = useState(true)

  return (
    <section id="pricing" className="relative py-24 sm:py-32 border-t border-white/[0.08] bg-black">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 relative">
        <CornerMarks />

        {/* Section Header */}
        <div className="mx-auto max-w-3xl text-center space-y-4 mb-12">
          <h2 className="text-3xl sm:text-5xl font-bold tracking-tight text-white">
            Simple pricing, powerful control plane
          </h2>
          <p className="text-neutral-400 text-base sm:text-lg">
            Deploy self-hosted for free, or upgrade to Team and Enterprise for distributed clusters.
          </p>

          {/* Billing Cycle Toggle */}
          <div className="inline-flex items-center gap-3 p-1 rounded-full border border-white/10 bg-neutral-950 mt-4">
            <button
              onClick={() => setAnnual(false)}
              className={`text-xs font-medium px-4 py-1.5 rounded-full transition ${
                !annual ? 'bg-white text-black font-semibold' : 'text-neutral-400 hover:text-white'
              }`}
            >
              Monthly
            </button>
            <button
              onClick={() => setAnnual(true)}
              className={`text-xs font-medium px-4 py-1.5 rounded-full transition flex items-center gap-1.5 ${
                annual ? 'bg-white text-black font-semibold' : 'text-neutral-400 hover:text-white'
              }`}
            >
              Annual
              <span className="text-[10px] px-1.5 py-0.2 rounded-full bg-emerald-500/20 text-emerald-300 font-mono">
                Save 20%
              </span>
            </button>
          </div>
        </div>

        {/* 3 Pricing Cards */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Free / Community */}
          <div className="rounded-3xl border border-white/10 bg-neutral-950/70 p-8 flex flex-col justify-between">
            <div>
              <span className="text-xs font-mono uppercase text-neutral-400">Community</span>
              <h3 className="text-2xl font-bold text-white mt-1">Self-Hosted</h3>
              <p className="text-xs text-neutral-400 mt-2">Perfect for local prototyping and single-machine services.</p>
              
              <div className="my-6">
                <span className="text-4xl font-extrabold text-white font-mono">$0</span>
                <span className="text-neutral-400 text-xs ml-2 font-mono">forever free</span>
              </div>

              <ul className="space-y-3 text-xs text-neutral-300">
                <li className="flex items-center gap-2">
                  <Check className="size-4 text-white" /> Full state machine & bounded execution
                </li>
                <li className="flex items-center gap-2">
                  <Check className="size-4 text-white" /> SQLite & PostgreSQL checkpoint storage
                </li>
                <li className="flex items-center gap-2">
                  <Check className="size-4 text-white" /> Human-in-the-loop review approvals
                </li>
                <li className="flex items-center gap-2">
                  <Check className="size-4 text-white" /> Offline mock replay & test suites
                </li>
                <li className="flex items-center gap-2">
                  <Check className="size-4 text-white" /> PII-redacted Failure Capsules
                </li>
              </ul>
            </div>

            <button
              onClick={() => onSelectPlan && onSelectPlan('community')}
              className="mt-8 w-full py-2.5 rounded-full border border-white/20 bg-white/5 text-white text-xs font-semibold hover:bg-white/10 transition"
            >
              Get Started Free
            </button>
          </div>

          {/* Pro / Team (Popular) */}
          <div className="rounded-3xl border border-white/30 bg-neutral-900/80 p-8 flex flex-col justify-between relative shadow-2xl">
            <div className="absolute -top-3.5 left-1/2 -translate-x-1/2 px-3 py-1 rounded-full bg-white text-black text-[10px] font-bold uppercase tracking-wider shadow-md">
              Most Popular
            </div>

            <div>
              <span className="text-xs font-mono uppercase text-neutral-300">Cloud / Team</span>
              <h3 className="text-2xl font-bold text-white mt-1">Production Pro</h3>
              <p className="text-xs text-neutral-400 mt-2">For startups and engineering teams deploying autonomous agents.</p>
              
              <div className="my-6">
                <span className="text-4xl font-extrabold text-white font-mono">
                  {annual ? '$24' : '$29'}
                </span>
                <span className="text-neutral-400 text-xs ml-2 font-mono">per seat / month</span>
              </div>

              <ul className="space-y-3 text-xs text-neutral-200">
                <li className="flex items-center gap-2">
                  <Check className="size-4 text-white" /> Everything in Community
                </li>
                <li className="flex items-center gap-2">
                  <Check className="size-4 text-white" /> Multi-worker distributed checkpoints
                </li>
                <li className="flex items-center gap-2">
                  <Check className="size-4 text-white" /> Slack & Email webhook approval channels
                </li>
                <li className="flex items-center gap-2">
                  <Check className="size-4 text-white" /> Unlimited monotonic event retention
                </li>
                <li className="flex items-center gap-2">
                  <Check className="size-4 text-white" /> Centralized Failure Capsule repository
                </li>
                <li className="flex items-center gap-2">
                  <Check className="size-4 text-white" /> CI/CD Trajectory regression suites
                </li>
              </ul>
            </div>

            <button
              onClick={() => onSelectPlan && onSelectPlan('pro')}
              className="mt-8 w-full py-2.5 rounded-full bg-white text-black text-xs font-bold hover:bg-neutral-200 transition active:scale-95 shadow-md"
            >
              Start 14-Day Free Trial
            </button>
          </div>

          {/* Enterprise */}
          <div className="rounded-3xl border border-white/10 bg-neutral-950/70 p-8 flex flex-col justify-between">
            <div>
              <span className="text-xs font-mono uppercase text-neutral-400">Enterprise</span>
              <h3 className="text-2xl font-bold text-white mt-1">Custom Dedicated</h3>
              <p className="text-xs text-neutral-400 mt-2">For large regulated organizations with custom security policies.</p>
              
              <div className="my-6">
                <span className="text-4xl font-extrabold text-white font-mono">Custom</span>
                <span className="text-neutral-400 text-xs ml-2 font-mono">annual agreement</span>
              </div>

              <ul className="space-y-3 text-xs text-neutral-300">
                <li className="flex items-center gap-2">
                  <Check className="size-4 text-white" /> VPC or on-prem air-gapped deployment
                </li>
                <li className="flex items-center gap-2">
                  <Check className="size-4 text-white" /> Custom code-level Policy Gate rules
                </li>
                <li className="flex items-center gap-2">
                  <Check className="size-4 text-white" /> SOC 2 Type II compliance reports
                </li>
                <li className="flex items-center gap-2">
                  <Check className="size-4 text-white" /> Dedicated 99.99% Uptime SLA
                </li>
                <li className="flex items-center gap-2">
                  <Check className="size-4 text-white" /> 24/7 Priority engineering support
                </li>
              </ul>
            </div>

            <button
              onClick={() => onSelectPlan && onSelectPlan('enterprise')}
              className="mt-8 w-full py-2.5 rounded-full border border-white/20 bg-white/5 text-white text-xs font-semibold hover:bg-white/10 transition"
            >
              Contact Solutions Team
            </button>
          </div>

        </div>
      </div>
    </section>
  )
}
