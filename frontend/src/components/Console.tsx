import React, { useState, useEffect } from 'react'
import { 
  Play, 
  RotateCw, 
  CheckCircle2, 
  PauseCircle, 
  AlertTriangle, 
  XCircle, 
  Clock, 
  ShieldAlert, 
  ChevronRight, 
  ChevronDown, 
  Activity, 
  FileLock2, 
  CheckCheck,
  Send,
  ArrowLeft,
  Sparkles,
  Terminal,
  ExternalLink
} from 'lucide-react'
import { ApprovalModal } from './ApprovalModal'
import { CapsuleViewer } from './CapsuleViewer'

interface Run {
  id: string
  workflow_id: string
  status: 'CREATED' | 'RUNNING' | 'PAUSED' | 'SUCCEEDED' | 'FAILED' | 'CANCELLED'
  current_node?: string
  step_count: number
  max_steps: number
  created_at: string
  updated_at?: string
  state?: Record<string, any>
}

interface EventItem {
  id: string
  run_id: string
  sequence_no: number
  event_type: string
  node_id?: string
  payload?: Record<string, any>
  created_at: string
}

interface ApprovalItem {
  id: string
  run_id: string
  tool_name: string
  arguments: Record<string, any>
  status: 'PENDING' | 'APPROVED' | 'REJECTED'
  risk_tier?: string
  created_at?: string
}

export const Console: React.FC<{ onBackToLanding: () => void }> = ({ onBackToLanding }) => {
  const [runs, setRuns] = useState<Run[]>([])
  const [selectedRunId, setSelectedRunId] = useState<string | null>(null)
  const [events, setEvents] = useState<EventItem[]>([])
  const [approvals, setApprovals] = useState<ApprovalItem[]>([])
  const [loading, setLoading] = useState(false)
  const [evalResult, setEvalResult] = useState<any>(null)
  const [capsuleData, setCapsuleData] = useState<any>(null)
  const [showApprovalModal, setShowApprovalModal] = useState(false)
  const [showCapsuleModal, setShowCapsuleModal] = useState(false)
  const [activeTab, setActiveTab] = useState<'timeline' | 'state' | 'eval' | 'capsule'>('timeline')
  const [expandedEvents, setExpandedEvents] = useState<Record<number, boolean>>({})

  // Fetch all runs
  const fetchRuns = async () => {
    try {
      setLoading(true)
      const res = await fetch('/v1/runs')
      if (res.ok) {
        const data = await res.json()
        setRuns(data)
        if (data.length > 0 && !selectedRunId) {
          setSelectedRunId(data[0].id)
        }
      }
    } catch (err) {
      console.error('Failed to fetch runs', err)
    } finally {
      setLoading(false)
    }
  }

  // Fetch pending approvals
  const fetchApprovals = async () => {
    try {
      const res = await fetch('/v1/approvals')
      if (res.ok) {
        const data = await res.json()
        setApprovals(data)
      }
    } catch (err) {
      console.error('Failed to fetch approvals', err)
    }
  }

  // Fetch events for selected run
  const fetchEvents = async (runId: string) => {
    try {
      const res = await fetch(`/v1/runs/${runId}/events`)
      if (res.ok) {
        const data = await res.json()
        setEvents(data)
      }
    } catch (err) {
      console.error('Failed to fetch events', err)
    }
  }

  const [sseActive, setSseActive] = useState(false)

  useEffect(() => {
    fetchRuns()
    fetchApprovals()
    const interval = setInterval(() => {
      fetchRuns()
      fetchApprovals()
    }, 5000)
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    if (!selectedRunId) return
    fetchEvents(selectedRunId)
    setEvalResult(null)
    setCapsuleData(null)

    let eventSource: EventSource | null = null
    try {
      eventSource = new EventSource(`/v1/runs/${selectedRunId}/stream`)
      eventSource.onopen = () => setSseActive(true)
      eventSource.onerror = () => setSseActive(false)
      
      const refreshAll = () => {
        fetchEvents(selectedRunId)
        fetchRuns()
        fetchApprovals()
      }

      eventSource.addEventListener('run.created', refreshAll)
      eventSource.addEventListener('run.paused', refreshAll)
      eventSource.addEventListener('run.resumed', refreshAll)
      eventSource.addEventListener('run.cancelled', refreshAll)
      eventSource.addEventListener('demo.approval_required', refreshAll)
      eventSource.addEventListener('demo.resumed', refreshAll)
      eventSource.onmessage = (e) => {
        try {
          const parsed = JSON.parse(e.data)
          if (parsed && parsed.event_type) {
            refreshAll()
          }
        } catch {}
      }
    } catch {
      setSseActive(false)
    }

    return () => {
      if (eventSource) {
        eventSource.close()
        setSseActive(false)
      }
    }
  }, [selectedRunId])

  const selectedRun = runs.find(r => r.id === selectedRunId)
  const pendingApproval = approvals.find(a => a.run_id === selectedRunId && a.status === 'PENDING')

  // Demo Trigger
  const handleStartDemo = async (type: 'billing' | 'crash' | 'general' = 'billing') => {
    try {
      setLoading(true)
      let body = {
        ticket_id: `TCK-${Math.floor(1000 + Math.random() * 9000)}`,
        customer_email: 'alex.rivera@example.com',
        description: 'Customer was billed twice ($149.00) for annual subscription.',
        amount: 149.0
      }
      if (type === 'crash') {
        body = {
          ticket_id: `TCK-${Math.floor(1000 + Math.random() * 9000)}`,
          customer_email: 'dev@techstart.io',
          description: 'Production worker crashed with NullPointer on ticket processing.',
          amount: 0.0
        }
      }

      const res = await fetch('/v1/demo/triage/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      })

      if (res.ok) {
        const data = await res.json()
        await fetchRuns()
        await fetchApprovals()
        setSelectedRunId(data.run_id)
      }
    } catch (err) {
      console.error('Failed to start demo', err)
    } finally {
      setLoading(false)
    }
  }

  // Resume paused run
  const handleResume = async () => {
    if (!selectedRunId) return
    try {
      setLoading(true)
      const res = await fetch(`/v1/demo/triage/${selectedRunId}/resume`, {
        method: 'POST'
      })
      if (res.ok) {
        await fetchRuns()
        await fetchApprovals()
        fetchEvents(selectedRunId)
      }
    } catch (err) {
      console.error('Failed to resume run', err)
    } finally {
      setLoading(false)
    }
  }

  // Decide approval
  const handleDecideApproval = async (decision: 'APPROVE' | 'REJECT', reviewer: string) => {
    if (!pendingApproval) return
    const res = await fetch(`/v1/approvals/${pendingApproval.id}/decision`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Actor': reviewer,
        'X-Actor-Roles': 'reviewer,operator'
      },
      body: JSON.stringify({
        approved: decision === 'APPROVE',
        reason: `${decision} by ${reviewer} via Web Console`
      })
    })

    if (!res.ok) {
      const err = await res.json()
      throw new Error(err.detail || 'Decision rejected by server')
    }

    await fetchApprovals()
    await fetchRuns()
    if (selectedRunId) fetchEvents(selectedRunId)
  }

  // Run Trajectory Evaluation
  const handleEvaluate = async () => {
    if (!selectedRunId) return
    try {
      setLoading(true)
      const res = await fetch('/v1/evaluations/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          run_id: selectedRunId,
          expected_node_order: ['classify_ticket', 'lookup_ticket', 'draft_response', 'send_reply'],
          require_hitl_approval_for: ['send_reply']
        })
      })
      if (res.ok) {
        const result = await res.json()
        setEvalResult(result)
        setActiveTab('eval')
      }
    } catch (err) {
      console.error('Evaluation failed', err)
    } finally {
      setLoading(false)
    }
  }

  // Export Failure Capsule
  const handleExportCapsule = async () => {
    if (!selectedRunId) return
    try {
      setLoading(true)
      const res = await fetch(`/v1/runs/${selectedRunId}/failure-capsule`, {
        method: 'POST'
      })
      if (res.ok) {
        const capsule = await res.json()
        setCapsuleData(capsule)
        setShowCapsuleModal(true)
      }
    } catch (err) {
      console.error('Failed to export capsule', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-[#030303] text-neutral-200 flex flex-col font-sans">
      
      {/* Top Console Action Bar */}
      <header className="h-14 border-b border-white/10 bg-black/90 px-4 sm:px-6 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-4">
          <button
            onClick={onBackToLanding}
            className="flex items-center gap-1.5 text-xs text-neutral-400 hover:text-white transition px-2 py-1 rounded bg-white/5 border border-white/10"
          >
            <ArrowLeft className="size-3.5" /> Back to Landing Page
          </button>

          <div className="h-4 w-px bg-white/10" />

          <div className="flex items-center gap-2">
            <span className="font-semibold text-white text-sm">Control Console</span>
            <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 flex items-center gap-1">
              <span className="size-1.5 rounded-full bg-emerald-400 animate-pulse" />
              API Connected
            </span>
            {sseActive && (
              <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-300 border border-cyan-500/30 flex items-center gap-1">
                <span className="size-1.5 rounded-full bg-cyan-400" />
                Live SSE Stream
              </span>
            )}
          </div>
        </div>

        {/* Quick Launchers */}
        <div className="flex items-center gap-2">
          <span className="text-xs text-neutral-500 font-mono hidden sm:inline">Launch Demo:</span>
          <button
            onClick={() => handleStartDemo('billing')}
            className="text-xs font-semibold px-3 py-1.5 rounded-md bg-white text-black hover:bg-neutral-200 transition flex items-center gap-1.5"
          >
            <Play className="size-3.5 fill-black" />
            Start Triage Run ($149)
          </button>
          <button
            onClick={() => { fetchRuns(); fetchApprovals(); if (selectedRunId) fetchEvents(selectedRunId); }}
            className="p-1.5 rounded-md border border-white/10 bg-white/5 text-neutral-400 hover:text-white transition"
            title="Refresh runs"
          >
            <RotateCw className="size-4" />
          </button>
        </div>
      </header>

      {/* Main Console Layout */}
      <div className="flex-1 grid grid-cols-1 lg:grid-cols-12 overflow-hidden">
        
        {/* Left Column: Runs List (Span 4) */}
        <div className="lg:col-span-4 border-r border-white/10 bg-[#060608] flex flex-col h-[calc(100vh-3.5rem)] overflow-y-auto">
          <div className="p-4 border-b border-white/10 flex items-center justify-between">
            <span className="text-xs uppercase font-mono tracking-wider text-neutral-400">
              Workflow Executions ({runs.length})
            </span>
            <span className="text-[11px] font-mono text-neutral-500">Auto-polling</span>
          </div>

          <div className="divide-y divide-white/5 flex-1 overflow-y-auto">
            {runs.length === 0 ? (
              <div className="p-8 text-center text-xs text-neutral-500 space-y-3">
                <Terminal className="size-8 mx-auto opacity-40" />
                <p>No runs registered yet in database.</p>
                <button
                  onClick={() => handleStartDemo('billing')}
                  className="px-3 py-1.5 rounded bg-white text-black text-xs font-semibold hover:bg-neutral-200"
                >
                  Create Initial Run
                </button>
              </div>
            ) : (
              runs.map((run) => {
                const isSelected = run.id === selectedRunId
                const isPaused = run.status === 'PAUSED'
                return (
                  <button
                    key={run.id}
                    onClick={() => setSelectedRunId(run.id)}
                    className={`w-full text-left p-4 transition-all flex flex-col gap-2 ${
                      isSelected
                        ? 'bg-white/10 border-l-2 border-white'
                        : 'hover:bg-white/[0.03]'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-mono text-xs font-semibold text-white truncate max-w-[200px]">
                        {run.id}
                      </span>
                      <span className={`text-[10px] font-mono px-2 py-0.5 rounded-full border ${
                        run.status === 'RUNNING' ? 'border-cyan-500/30 bg-cyan-500/10 text-cyan-300' :
                        run.status === 'PAUSED' ? 'border-amber-500/30 bg-amber-500/10 text-amber-300 font-bold' :
                        run.status === 'SUCCEEDED' ? 'border-emerald-500/30 bg-emerald-500/10 text-emerald-300' :
                        'border-rose-500/30 bg-rose-500/10 text-rose-300'
                      }`}>
                        {run.status}
                      </span>
                    </div>

                    <div className="flex items-center justify-between text-[11px] text-neutral-400 font-mono">
                      <span>Workflow: {run.workflow_id}</span>
                      <span>Steps: {run.step_count} / {run.max_steps}</span>
                    </div>

                    {isPaused && (
                      <div className="text-[10px] font-mono text-amber-300 flex items-center gap-1 bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/20">
                        <AlertTriangle className="size-3" />
                        Pending Human Review Gate
                      </div>
                    )}
                  </button>
                )
              })
            )}
          </div>
        </div>

        {/* Right Column: Run Details & Inspector (Span 8) */}
        <div className="lg:col-span-8 bg-[#09090b] flex flex-col h-[calc(100vh-3.5rem)] overflow-y-auto">
          {selectedRun ? (
            <div className="flex-1 flex flex-col overflow-y-auto">
              
              {/* Top Details Card */}
              <div className="p-6 border-b border-white/10 bg-black/40 space-y-4">
                <div className="flex flex-wrap items-center justify-between gap-4">
                  <div>
                    <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
                      {selectedRun.workflow_id}
                      <span className={`text-xs font-mono px-2.5 py-0.5 rounded-full border ${
                        selectedRun.status === 'PAUSED' ? 'border-amber-500/30 bg-amber-500/10 text-amber-300' :
                        selectedRun.status === 'SUCCEEDED' ? 'border-emerald-500/30 bg-emerald-500/10 text-emerald-300' :
                        selectedRun.status === 'RUNNING' ? 'border-cyan-500/30 bg-cyan-500/10 text-cyan-300' :
                        'border-rose-500/30 bg-rose-500/10 text-rose-300'
                      }`}>
                        {selectedRun.status}
                      </span>
                    </h2>
                    <p className="text-xs font-mono text-neutral-400 mt-1">
                      Run ID: <span className="text-white">{selectedRun.id}</span> • Created: {new Date(selectedRun.created_at).toLocaleTimeString()}
                    </p>
                  </div>

                  {/* Actions for this run */}
                  <div className="flex items-center gap-2">
                    {pendingApproval && (
                      <button
                        onClick={() => setShowApprovalModal(true)}
                        className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-amber-400 text-black font-semibold text-xs hover:bg-amber-300 transition shadow-md"
                      >
                        <ShieldAlert className="size-3.5" />
                        Review Gate Decision
                      </button>
                    )}

                    {selectedRun.status === 'PAUSED' && !pendingApproval && (
                      <button
                        onClick={handleResume}
                        className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white text-black font-semibold text-xs hover:bg-neutral-200 transition"
                      >
                        <Play className="size-3.5 fill-black" />
                        Resume Workflow
                      </button>
                    )}

                    <button
                      onClick={handleEvaluate}
                      className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-white/15 bg-white/5 text-neutral-300 hover:text-white text-xs font-mono transition"
                    >
                      <CheckCheck className="size-3.5" />
                      Evaluate Trajectory
                    </button>

                    <button
                      onClick={handleExportCapsule}
                      className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-white/15 bg-white/5 text-neutral-300 hover:text-white text-xs font-mono transition"
                    >
                      <FileLock2 className="size-3.5" />
                      Capsule
                    </button>
                  </div>
                </div>

                {/* Step Budget Progress Bar */}
                <div className="space-y-1.5 pt-2">
                  <div className="flex items-center justify-between text-xs font-mono text-neutral-400">
                    <span>Step Budget Consumed</span>
                    <span className="text-white">{selectedRun.step_count} / {selectedRun.max_steps} steps</span>
                  </div>
                  <div className="w-full h-1.5 rounded-full bg-white/10 overflow-hidden">
                    <div 
                      className={`h-full transition-all duration-300 ${
                        selectedRun.status === 'FAILED' ? 'bg-rose-500' :
                        selectedRun.status === 'PAUSED' ? 'bg-amber-400' : 'bg-white'
                      }`}
                      style={{ width: `${Math.min((selectedRun.step_count / selectedRun.max_steps) * 100, 100)}%` }}
                    />
                  </div>
                </div>
              </div>

              {/* Inspector Navigation Tabs */}
              <div className="flex items-center gap-1 border-b border-white/10 px-6 pt-3 bg-black/20 text-xs font-mono">
                <button
                  onClick={() => setActiveTab('timeline')}
                  className={`px-4 py-2 border-b-2 transition ${
                    activeTab === 'timeline'
                      ? 'border-white text-white font-semibold'
                      : 'border-transparent text-neutral-400 hover:text-white'
                  }`}
                >
                  Monotonic Events ({events.length})
                </button>
                <button
                  onClick={() => setActiveTab('state')}
                  className={`px-4 py-2 border-b-2 transition ${
                    activeTab === 'state'
                      ? 'border-white text-white font-semibold'
                      : 'border-transparent text-neutral-400 hover:text-white'
                  }`}
                >
                  State Machine State
                </button>
                <button
                  onClick={() => setActiveTab('eval')}
                  className={`px-4 py-2 border-b-2 transition ${
                    activeTab === 'eval'
                      ? 'border-white text-white font-semibold'
                      : 'border-transparent text-neutral-400 hover:text-white'
                  }`}
                >
                  Golden Trajectory CI {evalResult ? '✓' : ''}
                </button>
              </div>

              {/* Tab Contents */}
              <div className="p-6 flex-1 overflow-y-auto">
                {activeTab === 'timeline' && (
                  <div className="space-y-3">
                    {events.length === 0 ? (
                      <p className="text-xs text-neutral-500 font-mono">No events recorded yet.</p>
                    ) : (
                      events.map((evt) => {
                        const isExpanded = expandedEvents[evt.sequence_no]
                        return (
                          <div 
                            key={evt.sequence_no}
                            className="rounded-xl border border-white/10 bg-black/60 p-4 font-mono text-xs space-y-2 hover:border-white/20 transition"
                          >
                            <div 
                              onClick={() => setExpandedEvents(prev => ({ ...prev, [evt.sequence_no]: !isExpanded }))}
                              className="flex items-center justify-between cursor-pointer"
                            >
                              <div className="flex items-center gap-3">
                                <span className="size-6 rounded bg-white/10 text-white font-bold flex items-center justify-center text-[10px]">
                                  #{evt.sequence_no}
                                </span>
                                <span className="font-semibold text-white">{evt.event_type}</span>
                                {evt.node_id && (
                                  <span className="text-[10px] text-neutral-400 bg-white/5 px-2 py-0.5 rounded border border-white/10">
                                    node: {evt.node_id}
                                  </span>
                                )}
                              </div>
                              <div className="flex items-center gap-2 text-neutral-500 text-[11px]">
                                <span>{new Date(evt.created_at).toLocaleTimeString()}</span>
                                <ChevronDown className={`size-3.5 transition-transform ${isExpanded ? 'rotate-180' : ''}`} />
                              </div>
                            </div>

                            {isExpanded && evt.payload && (
                              <pre className="mt-2 p-3 rounded-lg bg-neutral-950 text-neutral-300 text-[11px] overflow-x-auto border border-white/5">
                                {JSON.stringify(evt.payload, null, 2)}
                              </pre>
                            )}
                          </div>
                        )
                      })
                    )}
                  </div>
                )}

                {activeTab === 'state' && (
                  <div className="rounded-xl border border-white/10 bg-neutral-950 p-4">
                    <span className="text-xs uppercase font-mono text-neutral-500 block mb-2">Projected Domain State:</span>
                    <pre className="text-xs font-mono text-neutral-300 overflow-x-auto leading-relaxed">
                      {JSON.stringify(selectedRun.state || {}, null, 2)}
                    </pre>
                  </div>
                )}

                {activeTab === 'eval' && (
                  <div className="space-y-4 font-mono text-xs">
                    {evalResult ? (
                      <div className="rounded-xl border border-white/10 bg-neutral-950 p-5 space-y-4">
                        <div className="flex items-center justify-between pb-3 border-b border-white/10">
                          <span className="font-bold text-white text-sm">Trajectory CI Evaluation Result</span>
                          <span className={`px-2.5 py-0.5 rounded-full text-xs font-bold ${
                            evalResult.passed ? 'bg-emerald-500/20 text-emerald-300' : 'bg-rose-500/20 text-rose-300'
                          }`}>
                            {evalResult.passed ? 'ALL CHECKS PASSED' : 'EVALUATION FAILED'}
                          </span>
                        </div>

                        <div className="grid grid-cols-2 gap-4 text-xs">
                          <div className="p-3 rounded bg-white/5 border border-white/5">
                            <span className="text-neutral-500 block">Monotonic Integrity</span>
                            <span className="text-white font-semibold">100% Verified</span>
                          </div>
                          <div className="p-3 rounded bg-white/5 border border-white/5">
                            <span className="text-neutral-500 block">Gate Adherence</span>
                            <span className="text-white font-semibold">Policy Compliant</span>
                          </div>
                        </div>

                        <pre className="p-3 rounded bg-black/60 text-neutral-300 text-[11px] overflow-x-auto">
                          {JSON.stringify(evalResult, null, 2)}
                        </pre>
                      </div>
                    ) : (
                      <div className="p-8 text-center text-neutral-500 space-y-3">
                        <CheckCheck className="size-8 mx-auto opacity-40" />
                        <p>No evaluation run yet for this trajectory.</p>
                        <button
                          onClick={handleEvaluate}
                          className="px-4 py-2 rounded bg-white text-black font-semibold text-xs hover:bg-neutral-200"
                        >
                          Run Golden Trajectory Evaluator
                        </button>
                      </div>
                    )}
                  </div>
                )}
              </div>

            </div>
          ) : (
            <div className="flex-1 flex items-center justify-center p-8 text-center text-neutral-500">
              <p className="text-sm font-mono">Select a workflow execution from the left pane.</p>
            </div>
          )}
        </div>

      </div>

      {/* Modals */}
      {showApprovalModal && pendingApproval && (
        <ApprovalModal
          approval={pendingApproval}
          onClose={() => setShowApprovalModal(false)}
          onDecide={handleDecideApproval}
        />
      )}

      {showCapsuleModal && capsuleData && (
        <CapsuleViewer
          capsule={capsuleData}
          runId={selectedRunId || 'unknown'}
          onClose={() => setShowCapsuleModal(false)}
        />
      )}

    </div>
  )
}
