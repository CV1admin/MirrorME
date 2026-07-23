import React, { useEffect, useMemo, useState } from 'react';

const MODEL_CONFIG_KEY = 'mirrorme_model_config';
const HANDSHAKE_SESSION_KEY = 'mirrorme_handshake_session_id';

interface ClaimDraftPayload {
  claim_id: string;
  statement: string;
  layer: string;
  status: string;
  source_id: string;
  source_hash: string;
  confidence: number;
  falsification_criterion: string;
}

interface ClaimRecordPayload {
  sequence: number;
  record_hash: string;
  draft: ClaimDraftPayload;
}

interface V04Status {
  version: string;
  codename: string;
  protocol: string;
  claims: {
    count: number;
    head_hash: string | null;
    integrity_valid: boolean;
    by_layer: Record<string, number>;
  };
  evolution: {
    proposal_count: number;
    evaluation_count: number;
    approval_count: number;
    proposal_chain_valid: boolean;
    review_threshold: number;
  };
  automatic_self_modification: boolean;
  execution_authorized: boolean;
  external_actions: boolean;
  truth_boundary: string;
}

interface ProposalResponse {
  ok: boolean;
  proposal: {
    proposal_id: string;
    proposal_hash: string;
    state: string;
  };
  execution_authorized: boolean;
}

interface EvaluationResponse {
  ok: boolean;
  evaluation: {
    proposal_id: string;
    evaluation_hash: string;
    overall_score: number;
    decision: string;
    reasons: string[];
  };
  execution_authorized: boolean;
}

interface ApprovalResponse {
  ok: boolean;
  approval: {
    approval_hash: string;
    reviewer: string;
    execution_authorized: boolean;
  };
  change_packet: {
    packet_hash: string;
    allowed_next_step: string;
    execution_authorized: boolean;
  };
  execution_authorized: boolean;
}

const readBridgeEndpoint = (): string => {
  try {
    const raw = window.localStorage.getItem(MODEL_CONFIG_KEY);
    if (!raw) return 'http://localhost:8765';
    const parsed = JSON.parse(raw) as { ollamaEndpoint?: unknown };
    if (typeof parsed.ollamaEndpoint === 'string' && parsed.ollamaEndpoint.trim()) {
      return parsed.ollamaEndpoint.replace(/\/$/, '');
    }
  } catch {
    // Fall through to the loopback default.
  }
  return 'http://localhost:8765';
};

const shortHash = (value: string | null | undefined): string => {
  if (!value) return 'none';
  return value.length > 22 ? `${value.slice(0, 14)}…${value.slice(-6)}` : value;
};

const MKultraV04: React.FC = () => {
  const [bridgeBase] = useState<string>(() => readBridgeEndpoint());
  const [status, setStatus] = useState<V04Status | null>(null);
  const [claims, setClaims] = useState<ClaimRecordPayload[]>([]);
  const [selectedClaim, setSelectedClaim] = useState('TL-MIRROR-ENGINE-SCAFFOLD-001');
  const [objective, setObjective] = useState('Add an inspectable MKultra v0.4 diagnostics capability');
  const [target, setTarget] = useState('ui');
  const [proposalId, setProposalId] = useState('');
  const [result, setResult] = useState<Record<string, unknown> | null>(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const sessionId = useMemo(
    () => window.localStorage.getItem(HANDSHAKE_SESSION_KEY) || '',
    [],
  );

  const refresh = async (): Promise<void> => {
    setLoading(true);
    setError('');
    try {
      const [statusResponse, claimsResponse] = await Promise.all([
        fetch(`${bridgeBase}/api/v04/status`),
        fetch(`${bridgeBase}/api/v04/claims`),
      ]);
      const statusPayload = await statusResponse.json() as V04Status & { error?: string };
      const claimsPayload = await claimsResponse.json() as { claims?: ClaimRecordPayload[]; error?: string };
      if (!statusResponse.ok) throw new Error(statusPayload.error || 'v04_status_failed');
      if (!claimsResponse.ok) throw new Error(claimsPayload.error || 'v04_claims_failed');
      setStatus(statusPayload);
      setClaims(claimsPayload.claims || []);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : String(caught));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void refresh();
  }, []);

  const post = async <T,>(path: string, payload: Record<string, unknown>): Promise<T> => {
    if (!sessionId) {
      throw new Error('Verified local session required. Complete the handshake in MirrorME settings.');
    }
    const response = await fetch(`${bridgeBase}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ...payload, session_id: sessionId }),
    });
    const data = await response.json() as T & { detail?: string; error?: string };
    if (!response.ok) throw new Error(data.detail || data.error || `request_failed_${response.status}`);
    return data;
  };

  const createProposal = async (): Promise<void> => {
    setLoading(true);
    setError('');
    try {
      const response = await post<ProposalResponse>('/api/v04/evolution/propose', {
        objective,
        target_components: [target],
        evidence_claim_ids: [selectedClaim],
        predicted_benefit: 'Increase local inspectability without autonomous execution',
        risks: ['stale data', 'incorrect epistemic promotion'],
        test_plan: ['run Python unit tests', 'run TypeScript and Vite checks'],
        rollback_plan: ['revert the feature branch or pull request'],
        requested_changes: ['add bounded metadata and read-only diagnostics'],
      });
      setProposalId(response.proposal.proposal_id);
      setResult(response as unknown as Record<string, unknown>);
      await refresh();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : String(caught));
    } finally {
      setLoading(false);
    }
  };

  const evaluateProposal = async (): Promise<void> => {
    if (!proposalId) return;
    setLoading(true);
    setError('');
    try {
      const response = await post<EvaluationResponse>('/api/v04/evolution/evaluate', {
        proposal_id: proposalId,
        scores: {
          evidence: 0.82,
          testability: 0.90,
          reversibility: 0.95,
          safety: 0.95,
          integrity: 0.90,
        },
        reasons: ['bounded scope', 'explicit tests', 'explicit rollback'],
      });
      setResult(response as unknown as Record<string, unknown>);
      await refresh();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : String(caught));
    } finally {
      setLoading(false);
    }
  };

  const approvePacket = async (): Promise<void> => {
    if (!proposalId) return;
    setLoading(true);
    setError('');
    try {
      const response = await post<ApprovalResponse>('/api/v04/evolution/approve', {
        proposal_id: proposalId,
        reviewer: 'VIREAX',
        human_approved: true,
      });
      setResult(response as unknown as Record<string, unknown>);
      await refresh();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : String(caught));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 lg:p-8 max-w-7xl mx-auto space-y-6">
      <div className="flex flex-col lg:flex-row lg:items-end lg:justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-[0.3em] text-cyan-500 font-bold">Governed Thin Line</p>
          <h2 className="text-3xl font-black text-slate-100 mt-2">MKultra v0.4 Full Stack</h2>
          <p className="text-sm text-slate-400 mt-2 max-w-3xl">
            Provenance-backed claim inspection and human-governed evolution packets. This console never executes patches or updates weights, policies, identity, or external systems.
          </p>
        </div>
        <button
          type="button"
          onClick={() => void refresh()}
          disabled={loading}
          className="px-4 py-2 rounded-lg border border-cyan-500/30 text-cyan-400 text-xs font-bold hover:bg-cyan-500/10 disabled:opacity-40"
        >
          Refresh Local Runtime
        </button>
      </div>

      {error && (
        <div className="border border-rose-500/30 bg-rose-500/10 text-rose-300 rounded-xl p-4 text-sm">
          {error}
        </div>
      )}

      <section className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
        <Metric label="Version" value={status ? `${status.version} ${status.codename}` : 'offline'} />
        <Metric label="Claim Registry" value={status ? `${status.claims.count} / ${status.claims.integrity_valid ? 'valid' : 'invalid'}` : 'unknown'} />
        <Metric label="Proposal Chain" value={status ? `${status.evolution.proposal_count} / ${status.evolution.proposal_chain_valid ? 'valid' : 'invalid'}` : 'unknown'} />
        <Metric label="Execution Authority" value={status?.execution_authorized ? 'ENABLED' : 'DISABLED'} critical={status?.execution_authorized === true} />
      </section>

      <section className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5">
          <h3 className="text-sm font-bold uppercase tracking-widest text-slate-400">Epistemic Claim Registry</h3>
          <div className="mt-4 space-y-3 max-h-[520px] overflow-auto pr-1">
            {claims.map((record) => (
              <label
                key={record.draft.claim_id}
                className={`block rounded-xl border p-4 cursor-pointer transition-colors ${
                  selectedClaim === record.draft.claim_id
                    ? 'border-cyan-500/50 bg-cyan-500/5'
                    : 'border-slate-800 bg-slate-950 hover:border-slate-700'
                }`}
              >
                <div className="flex items-start gap-3">
                  <input
                    type="radio"
                    name="claim"
                    value={record.draft.claim_id}
                    checked={selectedClaim === record.draft.claim_id}
                    onChange={() => setSelectedClaim(record.draft.claim_id)}
                    className="mt-1"
                  />
                  <div className="min-w-0">
                    <div className="flex flex-wrap gap-2 mb-2">
                      <span className="text-[10px] font-black text-cyan-400">{record.draft.layer}</span>
                      <span className="text-[10px] font-black text-amber-400">{record.draft.status}</span>
                    </div>
                    <p className="text-sm text-slate-200">{record.draft.statement}</p>
                    <p className="text-xs text-slate-500 mt-2">Falsification: {record.draft.falsification_criterion}</p>
                    <p className="text-[10px] text-slate-600 mt-2 mono">{record.draft.source_id} · {shortHash(record.record_hash)}</p>
                  </div>
                </div>
              </label>
            ))}
          </div>
        </div>

        <div className="space-y-6">
          <section className="bg-slate-900 border border-slate-800 rounded-2xl p-5">
            <h3 className="text-sm font-bold uppercase tracking-widest text-slate-400">Governed Evolution Proposal</h3>
            <div className="mt-4 space-y-4">
              <label className="block">
                <span className="text-xs text-slate-500">Objective</span>
                <textarea
                  value={objective}
                  onChange={(event) => setObjective(event.target.value)}
                  className="mt-1 w-full min-h-24 bg-slate-950 border border-slate-800 rounded-lg p-3 text-sm text-slate-200"
                />
              </label>
              <label className="block">
                <span className="text-xs text-slate-500">Target component</span>
                <input
                  value={target}
                  onChange={(event) => setTarget(event.target.value)}
                  className="mt-1 w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-sm text-slate-200"
                />
              </label>
              <div className="flex flex-wrap gap-3">
                <button type="button" onClick={() => void createProposal()} disabled={loading} className="px-4 py-2 bg-cyan-500 text-slate-950 rounded-lg text-xs font-black disabled:opacity-40">
                  1. Create Proposal
                </button>
                <button type="button" onClick={() => void evaluateProposal()} disabled={loading || !proposalId} className="px-4 py-2 border border-indigo-500/40 text-indigo-300 rounded-lg text-xs font-black disabled:opacity-40">
                  2. Evaluate
                </button>
                <button type="button" onClick={() => void approvePacket()} disabled={loading || !proposalId} className="px-4 py-2 border border-emerald-500/40 text-emerald-300 rounded-lg text-xs font-black disabled:opacity-40">
                  3. Approve Export Packet
                </button>
              </div>
              <p className="text-[11px] text-slate-500">
                Verified local session: {sessionId ? shortHash(sessionId) : 'missing — complete the MirrorME handshake'}
              </p>
            </div>
          </section>

          <section className="bg-slate-900 border border-slate-800 rounded-2xl p-5">
            <h3 className="text-sm font-bold uppercase tracking-widest text-slate-400">Last Audit Packet</h3>
            <pre className="mt-4 max-h-80 overflow-auto rounded-xl bg-slate-950 border border-slate-800 p-4 text-[11px] text-slate-400 whitespace-pre-wrap break-all">
              {result ? JSON.stringify(result, null, 2) : 'No proposal packet generated.'}
            </pre>
          </section>
        </div>
      </section>

      <section className="rounded-2xl border border-amber-500/20 bg-amber-500/5 p-5">
        <p className="text-xs font-black uppercase tracking-widest text-amber-400">Authority boundary</p>
        <p className="text-sm text-slate-300 mt-2">
          {status?.truth_boundary || 'Approval produces metadata only. Human-reviewed Git operations remain required.'}
        </p>
        <p className="text-xs text-slate-500 mt-2 mono">Bridge: {bridgeBase} · Protocol: {status?.protocol || 'offline'}</p>
      </section>
    </div>
  );
};

interface MetricProps {
  label: string;
  value: string;
  critical?: boolean;
}

const Metric: React.FC<MetricProps> = ({ label, value, critical = false }) => (
  <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4">
    <p className="text-[10px] uppercase tracking-widest text-slate-500 font-bold">{label}</p>
    <p className={`mt-2 text-sm font-black break-words ${critical ? 'text-rose-400' : 'text-cyan-400'}`}>{value}</p>
  </div>
);

export default MKultraV04;
