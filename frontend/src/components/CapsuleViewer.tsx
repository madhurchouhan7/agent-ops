import React, { useState } from 'react'
import { FileLock2, X, Download, Copy, Check, ShieldCheck } from 'lucide-react'

interface CapsuleViewerProps {
  capsule: Record<string, any>
  runId: string
  onClose: () => void
}

export const CapsuleViewer: React.FC<CapsuleViewerProps> = ({ capsule, runId, onClose }) => {
  const [copied, setCopied] = useState(false)

  const handleCopy = () => {
    navigator.clipboard.writeText(JSON.stringify(capsule, null, 2))
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const handleDownload = () => {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(capsule, null, 2))
    const downloadAnchor = document.createElement('a')
    downloadAnchor.setAttribute("href", dataStr)
    downloadAnchor.setAttribute("download", `capsule-${runId}.json`)
    document.body.appendChild(downloadAnchor)
    downloadAnchor.click()
    downloadAnchor.remove()
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-fd-fade-in">
      <div className="relative w-full max-w-2xl rounded-2xl border border-white/20 bg-[#0a0a0c] p-6 shadow-2xl space-y-6">
        
        {/* Header */}
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className="size-10 rounded-xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
              <FileLock2 className="size-5" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-white tracking-tight">Redacted Failure Capsule</h3>
              <p className="text-xs font-mono text-neutral-400">Run: {runId}</p>
            </div>
          </div>
          <button 
            onClick={onClose}
            className="rounded-lg p-1.5 text-neutral-400 hover:text-white hover:bg-white/10 transition"
          >
            <X className="size-5" />
          </button>
        </div>

        {/* Redaction Notice */}
        <div className="flex items-center gap-2 p-3 rounded-xl border border-emerald-500/20 bg-emerald-500/5 text-emerald-300 text-xs font-mono">
          <ShieldCheck className="size-4 shrink-0 text-emerald-400" />
          <span>Security Notice: All sensitive bearer tokens, API keys, and customer emails have been sanitized with [REDACTED_SECRET].</span>
        </div>

        {/* JSON Preview */}
        <div className="relative">
          <pre className="p-4 rounded-xl border border-white/10 bg-neutral-950 text-neutral-300 text-xs font-mono max-h-96 overflow-y-auto leading-relaxed">
            {JSON.stringify(capsule, null, 2)}
          </pre>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center justify-between pt-2">
          <span className="text-xs text-neutral-500 font-mono">Safe for export and offline replay</span>
          <div className="flex items-center gap-3">
            <button
              onClick={handleCopy}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-white/15 bg-white/5 text-xs text-neutral-300 hover:text-white hover:bg-white/10 transition"
            >
              {copied ? <Check className="size-3.5 text-emerald-400" /> : <Copy className="size-3.5" />}
              {copied ? 'Copied JSON' : 'Copy JSON'}
            </button>
            <button
              onClick={handleDownload}
              className="inline-flex items-center gap-1.5 px-4 py-1.5 rounded-lg bg-white text-black text-xs font-semibold hover:bg-neutral-200 transition"
            >
              <Download className="size-3.5" />
              Download Capsule
            </button>
          </div>
        </div>

      </div>
    </div>
  )
}
