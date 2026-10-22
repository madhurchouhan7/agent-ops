import React from 'react'

export const Footer: React.FC = () => {
  return (
    <footer className="border-t border-white/[0.08] bg-black py-16 text-neutral-400 text-xs">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-2 md:grid-cols-5 gap-8 mb-12">
          
          {/* Brand Info */}
          <div className="col-span-2 space-y-4">
            <div className="flex items-center gap-2">
              <div className="size-6 rounded bg-white text-black font-bold flex items-center justify-center text-xs">
                A
              </div>
              <span className="font-semibold text-white text-sm tracking-tight">AgentOps</span>
            </div>
            <p className="text-neutral-400 max-w-sm leading-relaxed">
              Reliable, observable developer control plane for stateful AI agent workflows. Strict state machines, persistent timelines, and policy safety gates.
            </p>
            <div className="flex items-center gap-2 text-emerald-400 font-mono text-[11px]">
              <span className="size-2 rounded-full bg-emerald-400 animate-pulse" />
              All Systems Operational
            </div>
          </div>

          {/* Links Column 1: Platform */}
          <div className="space-y-3">
            <span className="font-semibold text-white block text-sm">Platform</span>
            <ul className="space-y-2">
              <li><a href="#features" className="hover:text-white transition">State Machine Runtime</a></li>
              <li><a href="#workflows" className="hover:text-white transition">Monotonic Timelines</a></li>
              <li><a href="#features" className="hover:text-white transition">Policy Gate & Approvals</a></li>
              <li><a href="#features" className="hover:text-white transition">Failure Capsules</a></li>
              <li><a href="#scale" className="hover:text-white transition">Mock Replay CI</a></li>
            </ul>
          </div>

          {/* Links Column 2: Resources */}
          <div className="space-y-3">
            <span className="font-semibold text-white block text-sm">Resources</span>
            <ul className="space-y-2">
              <li><a href="/docs" target="_blank" rel="noreferrer" className="hover:text-white transition">FastAPI Swagger Docs</a></li>
              <li><a href="/redoc" target="_blank" rel="noreferrer" className="hover:text-white transition">ReDoc Specifications</a></li>
              <li><a href="#faq" className="hover:text-white transition">FAQ & Troubleshooting</a></li>
              <li><a href="https://github.com" target="_blank" rel="noreferrer" className="hover:text-white transition">GitHub Repository</a></li>
            </ul>
          </div>

          {/* Links Column 3: Legal & Open Source */}
          <div className="space-y-3">
            <span className="font-semibold text-white block text-sm">Governance</span>
            <ul className="space-y-2">
              <li><span className="text-neutral-500">MIT Open Source License</span></li>
              <li><span className="text-neutral-500">Zero Cloud Telemetry</span></li>
              <li><span className="text-neutral-500">Local-First Storage</span></li>
              <li><span className="text-neutral-500">PII Data Scrubbing</span></li>
            </ul>
          </div>

        </div>

        {/* Bottom Bar */}
        <div className="pt-8 border-t border-white/5 flex flex-col sm:flex-row items-center justify-between gap-4 text-neutral-500">
          <p>© {new Date().getFullYear()} AgentOps Control Plane. Designed with minimal monochrome aesthetics.</p>
          <div className="flex items-center gap-6">
            <span>Built for Python 3.12+ & React</span>
            <span>Local SQLite & PostgreSQL Engine</span>
          </div>
        </div>
      </div>
    </footer>
  )
}
