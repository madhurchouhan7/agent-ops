import React, { useState } from 'react'
import { ShieldAlert, CheckCircle, XCircle, AlertTriangle, X } from 'lucide-react'

interface ApprovalModalProps {
  approval: {
    id: string
    run_id: string
    tool_name: string
    arguments: Record<string, any>
    risk_tier?: string
    created_at?: string
  }
  onClose: () => void
  onDecide: (decision: 'APPROVE' | 'REJECT', reviewer: string) => Promise<void>
}

export const ApprovalModal: React.FC<ApprovalModalProps> = ({ approval, onClose, onDecide }) => {
  const [reviewer, setReviewer] = useState('lead_engineer')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (decision: 'APPROVE' | 'REJECT') => {
    try {
      setLoading(true)
      setError(null)
      await onDecide(decision, reviewer)
      onClose()
    } catch (err: any) {
      setError(err?.message || 'Failed to submit decision')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-fd-fade-in">
      <div className="relative w-full max-w-lg rounded-2xl border border-white/20 bg-[#0a0a0c] p-6 shadow-2xl space-y-6">
        
        {/* Header */}
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className="size-10 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-amber-400">
              <ShieldAlert className="size-5" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-white tracking-tight">Review Protected Action</h3>
              <p className="text-xs font-mono text-neutral-400">Approval ID: {approval.id}</p>
            </div>
          </div>
          <button 
            onClick={onClose}
            className="rounded-lg p-1.5 text-neutral-400 hover:text-white hover:bg-white/10 transition"
          >
            <X className="size-5" />
          </button>
        </div>

        {/* Action summary */}
        <div className="rounded-xl border border-white/10 bg-black/60 p-4 space-y-3 text-xs font-mono">
          <div className="flex items-center justify-between text-neutral-400">
            <span>Target Tool:</span>
            <span className="text-white font-semibold bg-white/10 px-2 py-0.5 rounded">
              {approval.tool_name}
            </span>
          </div>

          <div className="flex items-center justify-between text-neutral-400">
            <span>Associated Run ID:</span>
            <span className="text-neutral-300 truncate max-w-[240px]">{approval.run_id}</span>
          </div>

          <div className="pt-2 border-t border-white/5">
            <span className="text-neutral-400 block mb-1">Payload Arguments:</span>
            <pre className="p-2.5 rounded-lg bg-neutral-950 text-neutral-300 text-[11px] overflow-x-auto max-h-40 border border-white/5">
              {JSON.stringify(approval.arguments, null, 2)}
            </pre>
          </div>
        </div>

        {/* Reviewer Input */}
        <div className="space-y-1.5 text-xs">
          <label className="text-neutral-400 font-medium block">
            Reviewer Identity / Role:
          </label>
          <input
            type="text"
            value={reviewer}
            onChange={(e) => setReviewer(e.target.value)}
            className="w-full rounded-lg border border-white/15 bg-neutral-900 px-3 py-2 text-sm text-white placeholder-neutral-500 focus:border-white focus:outline-none"
            placeholder="e.g. ops_reviewer_01"
          />
        </div>

        {error && (
          <div className="p-3 rounded-lg border border-rose-500/30 bg-rose-500/10 text-rose-300 text-xs">
            {error}
          </div>
        )}

        {/* Decision Actions */}
        <div className="flex items-center gap-3 pt-2">
          <button
            disabled={loading}
            onClick={() => handleSubmit('REJECT')}
            className="flex-1 inline-flex items-center justify-center gap-1.5 py-2.5 rounded-xl border border-rose-500/30 bg-rose-500/10 text-rose-300 font-semibold text-xs hover:bg-rose-500/20 transition disabled:opacity-50"
          >
            <XCircle className="size-4" />
            Reject Action
          </button>

          <button
            disabled={loading}
            onClick={() => handleSubmit('APPROVE')}
            className="flex-1 inline-flex items-center justify-center gap-1.5 py-2.5 rounded-xl bg-white text-black font-semibold text-xs hover:bg-neutral-200 transition disabled:opacity-50 shadow-md"
          >
            <CheckCircle className="size-4" />
            Authorize Execution
          </button>
        </div>

      </div>
    </div>
  )
}
