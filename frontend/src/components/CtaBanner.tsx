import React from 'react'
import { ArrowRight, Terminal } from 'lucide-react'
import { CornerMarks } from './CornerMarks'

interface CtaBannerProps {
  onLaunchConsole: () => void
  onStartDemo: () => void
}

export const CtaBanner: React.FC<CtaBannerProps> = ({ onLaunchConsole, onStartDemo }) => {
  return (
    <section className="relative py-28 sm:py-36 border-t border-white/[0.08] bg-black overflow-hidden text-center">
      {/* Signature Vertex Concentric Glowing Rings */}
      <div 
        aria-hidden="true" 
        className="pointer-events-none absolute -bottom-80 sm:-bottom-96 left-1/2 -translate-x-1/2 flex items-center justify-center"
        style={{ width: '800px', height: '800px' }}
      >
        {/* Outer Ring */}
        <div 
          className="absolute rounded-full border border-white/[0.08] bg-neutral-900/40 backdrop-blur-3xl shadow-[0_0_120px_rgba(255,255,255,0.08)]"
          style={{ width: '750px', height: '750px' }}
        />
        {/* Middle Ring */}
        <div 
          className="absolute rounded-full border border-white/[0.12] bg-neutral-950/60 shadow-[0_0_80px_rgba(255,255,255,0.06)]"
          style={{ width: '560px', height: '560px' }}
        />
        {/* Inner Ring */}
        <div 
          className="absolute rounded-full border border-white/20 bg-gradient-to-b from-white/10 to-transparent shadow-[0_0_40px_rgba(255,255,255,0.1)]"
          style={{ width: '380px', height: '380px' }}
        />
      </div>

      <div className="relative z-10 mx-auto max-w-4xl px-4 sm:px-6 lg:px-8 space-y-6">
        <h2 className="text-3xl sm:text-6xl font-bold tracking-tight text-white leading-tight">
          Connect your stack and <br />
          <span className="text-transparent bg-clip-text bg-gradient-to-b from-white to-neutral-400">
            govern agents today
          </span>
        </h2>

        <p className="mx-auto max-w-xl text-neutral-400 text-base sm:text-lg">
          Start with the local production-ready server and web console in under 30 seconds. No external infrastructure or cloud accounts required.
        </p>

        <div className="flex flex-wrap items-center justify-center gap-4 pt-4">
          <button
            onClick={onLaunchConsole}
            className="inline-flex items-center gap-2 text-sm font-semibold px-8 py-3.5 rounded-full bg-white text-black hover:bg-neutral-200 shadow-xl transition active:scale-95"
          >
            Launch Live Console
            <ArrowRight className="size-4" />
          </button>

          <button
            onClick={onStartDemo}
            className="inline-flex items-center gap-2 text-sm font-medium px-6 py-3.5 rounded-full border border-white/20 bg-neutral-900 text-white hover:bg-neutral-800 transition active:scale-95"
          >
            <Terminal className="size-4 text-neutral-400" />
            Trigger Support Demo
          </button>
        </div>

        <p className="text-xs font-mono text-neutral-500 pt-2">
          &gt; python -m agent_ops --port 8000
        </p>
      </div>
    </section>
  )
}
