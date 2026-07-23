import React from 'react';

const statusTone: Record<string, string> = {
  implemented: 'border-emerald-500/30 bg-emerald-500/10 text-emerald-300',
  development: 'border-amber-500/30 bg-amber-500/10 text-amber-300',
  blocked: 'border-red-500/30 bg-red-500/10 text-red-300',
  planned: 'border-slate-600 bg-slate-800/60 text-slate-300',
};

const StatusBadge: React.FC<{ status: keyof typeof statusTone; children?: React.ReactNode }> = ({ status, children }) => (
  <span className={`inline-flex rounded-full border px-2 py-1 text-[10px] font-bold uppercase tracking-wider ${statusTone[status]}`}>
    {children ?? status}
  </span>
);

const OiiidsOperationsDashboard: React.FC = () => {
  const processStages = [
    'Received',
    'Authenticated',
    'Node verified',
    'Authorized',
    'Validated',
    'Prepared',
    'Committed',
    'Audited',
    'Completed',
  ];

  const nodeCapabilities = [
    { label: 'Deterministic NodeID', status: 'implemented' as const, detail: 'Public-key-derived nodeid:cv1 identifier' },
    { label: 'Node lifecycle records', status: 'implemented' as const, detail: 'Pending, active, suspended, revoked and rejected states' },
    { label: 'Operation binding', status: 'implemented' as const, detail: 'Principal, NodeID, key, method, digest, session, nonce and timestamp' },
    { label: 'Live Ed25519 verification', status: 'planned' as const, detail: 'Proof model exists; cryptographic verifier is the next increment' },
    { label: 'Durable node registry', status: 'planned' as const, detail: 'SQLite/PostgreSQL persistence not yet connected' },
  ];

  const resourceCapabilities = [
    { label: 'Immutable resource envelopes', status: 'implemented' as const },
    { label: 'SHA-256 content integrity', status: 'implemented' as const },
    { label: 'Version and provenance chain', status: 'implemented' as const },
    { label: 'Selective mirroring', status: 'planned' as const },
    { label: 'CRDT reconciliation', status: 'planned' as const },
    { label: 'Encrypted payload adapter', status: 'planned' as const },
  ];

  const safetyGates = [
    { gate: 'Public network endpoint', state: 'blocked' as const, reason: 'Authenticated gateway and rate controls are not implemented.' },
    { gate: 'Member-facing production', state: 'blocked' as const, reason: 'Durable persistence, live asymmetric verification and recovery testing are required.' },
    { gate: 'Local development', state: 'development' as const, reason: 'Permitted for controlled testing with non-sensitive data.' },
    { gate: 'Repository integration tests', state: 'implemented' as const, reason: 'Integrity, access and NodeID process tests are available.' },
  ];

  return (
    <div className="mx-auto max-w-7xl space-y-6 p-6 lg:p-8">
      <header className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <div className="mb-2 flex items-center gap-2">
            <StatusBadge status="development">Development system</StatusBadge>
            <span className="text-xs text-slate-500">No live production telemetry</span>
          </div>
          <h2 className="text-3xl font-bold text-slate-100">OIIIDS Operations</h2>
          <p className="mt-2 max-w-3xl text-sm text-slate-400">
            MirrorME node identity, resource exchange, process orchestration and Civilisation.One integration status.
          </p>
        </div>
        <div className="rounded-xl border border-cyan-500/30 bg-cyan-500/10 px-5 py-3">
          <div className="text-[10px] font-bold uppercase tracking-widest text-cyan-400">Architecture boundary</div>
          <div className="mt-1 text-sm font-semibold text-cyan-200">MirrorME → authenticated gateway → OIIIDS</div>
        </div>
      </header>

      <section className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
          <div className="text-[10px] font-bold uppercase tracking-widest text-slate-500">NodeID core</div>
          <div className="mt-3 text-2xl font-black text-emerald-300">Implemented</div>
          <p className="mt-2 text-xs text-slate-500">Identifier and lifecycle value models</p>
        </div>
        <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
          <div className="text-[10px] font-bold uppercase tracking-widest text-slate-500">Process states</div>
          <div className="mt-3 text-2xl font-black text-cyan-300">9-stage</div>
          <p className="mt-2 text-xs text-slate-500">Guarded, auditable transition path</p>
        </div>
        <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
          <div className="text-[10px] font-bold uppercase tracking-widest text-slate-500">Resource core</div>
          <div className="mt-3 text-2xl font-black text-emerald-300">Active</div>
          <p className="mt-2 text-xs text-slate-500">Local and integration testing only</p>
        </div>
        <div className="rounded-2xl border border-red-500/20 bg-red-500/5 p-5">
          <div className="text-[10px] font-bold uppercase tracking-widest text-red-400">Production gate</div>
          <div className="mt-3 text-2xl font-black text-red-300">Closed</div>
          <p className="mt-2 text-xs text-red-300/70">Do not expose directly to the internet</p>
        </div>
      </section>

      <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
        <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
          <div>
            <h3 className="text-xs font-bold uppercase tracking-widest text-cyan-400">Resource publication process</h3>
            <p className="mt-1 text-xs text-slate-500">Reference state machine; not a live queue.</p>
          </div>
          <StatusBadge status="implemented">Process model implemented</StatusBadge>
        </div>
        <div className="grid grid-cols-1 gap-2 md:grid-cols-3 xl:grid-cols-9">
          {processStages.map((stage, index) => (
            <div key={stage} className="relative rounded-xl border border-slate-800 bg-slate-950 p-3 text-center">
              <div className="text-[10px] font-mono text-slate-600">{String(index + 1).padStart(2, '0')}</div>
              <div className="mt-1 text-xs font-semibold text-slate-300">{stage}</div>
              {index < processStages.length - 1 && (
                <div className="absolute -right-2 top-1/2 hidden -translate-y-1/2 text-cyan-500 xl:block">→</div>
              )}
            </div>
          ))}
        </div>
      </section>

      <section className="grid grid-cols-1 gap-4 xl:grid-cols-2">
        <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
          <h3 className="mb-4 text-xs font-bold uppercase tracking-widest text-cyan-400">Node identity subsystem</h3>
          <div className="space-y-3">
            {nodeCapabilities.map((item) => (
              <div key={item.label} className="rounded-xl border border-slate-800 bg-slate-950 p-4">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <h4 className="text-sm font-semibold text-slate-200">{item.label}</h4>
                    <p className="mt-1 text-xs text-slate-500">{item.detail}</p>
                  </div>
                  <StatusBadge status={item.status} />
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
          <h3 className="mb-4 text-xs font-bold uppercase tracking-widest text-cyan-400">Resource exchange subsystem</h3>
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            {resourceCapabilities.map((item) => (
              <div key={item.label} className="rounded-xl border border-slate-800 bg-slate-950 p-4">
                <div className="mb-3"><StatusBadge status={item.status} /></div>
                <h4 className="text-sm font-semibold text-slate-200">{item.label}</h4>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
        <h3 className="mb-4 text-xs font-bold uppercase tracking-widest text-cyan-400">Deployment and safety gates</h3>
        <div className="overflow-hidden rounded-xl border border-slate-800">
          <div className="hidden grid-cols-[1.1fr_0.7fr_2fr] gap-4 border-b border-slate-800 bg-slate-950 px-4 py-3 text-[10px] font-bold uppercase tracking-widest text-slate-500 md:grid">
            <div>Gate</div><div>Status</div><div>Reason</div>
          </div>
          {safetyGates.map((item) => (
            <div key={item.gate} className="grid grid-cols-1 gap-2 border-b border-slate-800 px-4 py-4 last:border-0 md:grid-cols-[1.1fr_0.7fr_2fr] md:items-center md:gap-4">
              <div className="text-sm font-semibold text-slate-200">{item.gate}</div>
              <div><StatusBadge status={item.state} /></div>
              <div className="text-xs text-slate-500">{item.reason}</div>
            </div>
          ))}
        </div>
      </section>

      <section className="rounded-2xl border border-amber-500/20 bg-amber-500/5 p-5">
        <h3 className="text-sm font-bold text-amber-300">Safe-use boundary</h3>
        <p className="mt-2 text-sm text-amber-100/70">
          This screen reports repository implementation status. It must not be interpreted as evidence that a node is authenticated,
          a resource is scientifically valid, or the service is ready for member-facing production.
        </p>
      </section>
    </div>
  );
};

export default OiiidsOperationsDashboard;
