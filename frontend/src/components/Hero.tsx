import React from 'react'
import { Sparkles, ArrowRight, Terminal, ShieldAlert, Cpu } from 'lucide-react'
import { HeroWorkflowSwitcher } from './HeroWorkflowSwitcher'
import { CornerMarks } from './CornerMarks'

interface HeroProps {
  onLaunchConsole: () => void
  onStartDemo: () => void
}

export const Hero: React.FC<HeroProps> = ({ onLaunchConsole, onStartDemo }) => {
  return (
    <section className="relative pt-16 pb-20 md:pt-24 md:pb-28 overflow-hidden">
      {/* Background radial gradient glow */}
      <div 
        aria-hidden="true" 
        className="pointer-events-none absolute -top-40 left-1/2 -translate-x-1/2 size-[650px] rounded-full bg-gradient-to-b from-white/[0.08] via-white/[0.02] to-transparent blur-3xl"
      />

      {/* Main Hero Container with Corner Crosshairs */}
      <div className="relative mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="relative border border-white/[0.08] bg-black/40 rounded-3xl p-6 sm:p-10 md:p-14 backdrop-blur-sm">
          <CornerMarks />

          {/* Centered Heading Content */}
          <div className="mx-auto max-w-4xl text-center space-y-6">
            {/* Pill Badge */}
            <div className="inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/[0.04] px-3.5 py-1.5 text-xs text-neutral-300 backdrop-blur-md shadow-sm">
              <Sparkles className="size-3.5 text-white" />
              <span className="font-medium text-white">AI-Native Agent Observability & Governance</span>
              <span className="text-neutral-500">•</span>
              <span className="text-neutral-400">Strict State Machine Runtime</span>
            </div>

            {/* Main Headline */}
            <h1 className="text-4xl sm:text-6xl lg:text-7xl font-bold tracking-tight text-white leading-[1.08]">
              Automate and govern <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-b from-white via-neutral-200 to-neutral-500">
                stateful AI agents
              </span>
            </h1>

            {/* Subtitle */}
            <p className="mx-auto max-w-2xl text-base sm:text-lg text-neutral-400 leading-relaxed font-normal">
              Connect your tools, enforce code-level policy gates, and let agents run with strict state transitions, persistent timelines, human approvals, and deterministic offline replay.
            </p>

            {/* Dual CTAs */}
            <div className="flex flex-wrap items-center justify-center gap-4 pt-2">
              <button
                onClick={onLaunchConsole}
                className="inline-flex items-center gap-2 text-sm font-semibold px-6 py-3 rounded-full bg-white text-black hover:bg-neutral-200 shadow-lg shadow-white/5 transition active:scale-95"
              >
                Launch Live Console
                <ArrowRight className="size-4" />
              </button>

              <button
                onClick={onStartDemo}
                className="inline-flex items-center gap-2 text-sm font-medium px-6 py-3 rounded-full border border-white/15 bg-neutral-900/80 text-white hover:bg-neutral-800 hover:border-white/30 transition active:scale-95"
              >
                <Terminal className="size-4 text-neutral-400" />
                Run Support Triage Demo
              </button>
            </div>

            {/* Small trust caption */}
            <p className="text-xs font-mono text-neutral-500 pt-1">
              Zero external network telemetry • SQLite/PostgreSQL durable storage • Fully self-hosted
            </p>
          </div>

          {/* Interactive Agent Run Switcher Card */}
          <div className="mt-12 sm:mt-16">
            <HeroWorkflowSwitcher />
          </div>
        </div>
      </div>
    </section>
  )
}
