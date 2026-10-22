import React from 'react'
import { CornerMarks } from './CornerMarks'

const LOGOS = [
  { name: 'Anthropic Claude', tag: 'AI Model' },
  { name: 'OpenAI GPT-4o', tag: 'AI Model' },
  { name: 'FastAPI', tag: 'Runtime' },
  { name: 'Python 3.12+', tag: 'Core Engine' },
  { name: 'PostgreSQL', tag: 'Durable Storage' },
  { name: 'SQLite', tag: 'Local Disk' },
  { name: 'GitHub', tag: 'CI/CD Gate' },
  { name: 'Linear', tag: 'Issue Tracker' },
  { name: 'Slack', tag: 'Approval Channel' },
  { name: 'Supabase', tag: 'Database' },
  { name: 'Docker', tag: 'Container' },
  { name: 'Notion', tag: 'Knowledge Base' },
]

export const TechMarquee: React.FC = () => {
  return (
    <section className="relative py-12 overflow-hidden border-y border-white/[0.08] bg-black/60">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 relative">
        <CornerMarks />
        
        <div className="text-center mb-6">
          <p className="text-xs font-mono uppercase tracking-widest text-neutral-500">
            Native Interoperability with Modern AI Stacks & Orchestrators
          </p>
        </div>

        {/* Marquee Wrapper with Gradient Fade Edges */}
        <div className="relative w-full overflow-hidden [mask-image:linear-gradient(to_right,transparent,white_20%,white_80%,transparent)]">
          <div className="flex w-max animate-marquee space-x-12 py-2">
            {[...LOGOS, ...LOGOS].map((item, idx) => (
              <div 
                key={idx} 
                className="flex items-center gap-3 px-4 py-2 rounded-lg border border-white/5 bg-white/[0.02] hover:bg-white/[0.05] transition cursor-default"
              >
                <div className="size-2 rounded-full bg-white/40" />
                <span className="font-semibold text-sm tracking-tight text-white whitespace-nowrap">
                  {item.name}
                </span>
                <span className="text-[10px] font-mono text-neutral-400 bg-white/5 px-1.5 py-0.5 rounded border border-white/10">
                  {item.tag}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}
