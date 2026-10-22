import React from 'react'
import { Terminal, ShieldCheck, ArrowRight, Github, ExternalLink } from 'lucide-react'

interface NavbarProps {
  currentView: 'landing' | 'console'
  onNavigate: (view: 'landing' | 'console') => void
  onStartDemo?: () => void
}

export const Navbar: React.FC<NavbarProps> = ({ currentView, onNavigate, onStartDemo }) => {
  return (
    <header className="sticky top-0 z-50 w-full border-b border-white/[0.08] bg-black/80 backdrop-blur-xl">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        {/* Brand Logo */}
        <div className="flex items-center gap-8">
          <button 
            onClick={() => onNavigate('landing')} 
            className="flex items-center gap-2.5 text-left group transition"
          >
            <div className="relative flex size-8 items-center justify-center rounded-lg border border-white/20 bg-neutral-900 shadow-inner group-hover:border-white/40 transition">
              {/* Geometric monochrome icon */}
              <div className="size-3.5 rounded-sm bg-white" />
              <div className="absolute inset-0 rounded-lg bg-gradient-to-tr from-white/10 to-transparent" />
            </div>
            <div className="flex flex-col">
              <span className="font-semibold text-base tracking-tight text-white flex items-center gap-1.5">
                AgentOps
                <span className="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded border border-white/20 text-neutral-400 bg-white/5">
                  v0.1
                </span>
              </span>
            </div>
          </button>

          {/* Navigation Links */}
          <nav className="hidden md:flex items-center gap-6 text-sm text-neutral-400 font-medium">
            <a href="#features" className="hover:text-white transition">Features</a>
            <a href="#workflows" className="hover:text-white transition">Workflows</a>
            <a href="#scale" className="hover:text-white transition">Scale</a>
            <a href="#pricing" className="hover:text-white transition">Pricing</a>
            <a href="#faq" className="hover:text-white transition">FAQ</a>
            <a href="/docs" target="_blank" rel="noreferrer" className="flex items-center gap-1 hover:text-white transition">
              API Docs <ExternalLink className="size-3 opacity-60" />
            </a>
          </nav>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-3">
          {currentView === 'landing' ? (
            <>
              <button
                onClick={() => {
                  onNavigate('console')
                  if (onStartDemo) onStartDemo()
                }}
                className="hidden sm:inline-flex items-center gap-1.5 text-xs font-mono font-medium px-3 py-1.5 rounded-md border border-white/15 bg-white/5 text-neutral-300 hover:text-white hover:bg-white/10 transition"
              >
                <Terminal className="size-3.5 text-white/70" />
                Quick Demo
              </button>
              
              <button
                onClick={() => onNavigate('console')}
                className="inline-flex items-center gap-2 text-sm font-medium px-4 py-2 rounded-full bg-white text-black hover:bg-neutral-200 shadow-sm transition active:scale-95"
              >
                Launch Console
                <ArrowRight className="size-4" />
              </button>
            </>
          ) : (
            <button
              onClick={() => onNavigate('landing')}
              className="inline-flex items-center gap-2 text-sm font-medium px-4 py-2 rounded-full border border-white/20 bg-neutral-900 text-white hover:bg-neutral-800 transition"
            >
              Back to Overview
            </button>
          )}
        </div>
      </div>
    </header>
  )
}
