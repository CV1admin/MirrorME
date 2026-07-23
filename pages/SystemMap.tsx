import React from 'react';

type MapNode = {
  title: string;
  status: 'implemented' | 'development' | 'planned' | 'blocked';
  detail: string;
  items: string[];
};

const statusStyle: Record<MapNode['status'], string> = {
  implemented: 'border-emerald-500/30 bg-emerald-500/10 text-emerald-300',
  development: 'border-amber-500/30 bg-amber-500/10 text-amber-300',
  planned: 'border-cyan-500/30 bg-cyan-500/10 text-cyan-300',
  blocked: 'border-red-500/30 bg-red-500/10 text-red-300',
};

const layers: { title: string; boundary: string; nodes: MapNode[] }[] = [
  {
    title: '1. Member and Local Node Layer',
    boundary: 'User-controlled, local-first execution boundary',
    nodes: [
      { title: 'MirrorME Dashboard', status: 'implemented', detail: 'React/TypeScript operational interface.', items: ['MirrorME workspace', 'OIIIDS operations', 'System status', 'Simulation controls'] },
      { title: 'Local Model Runtime', status: 'development', detail: 'Ollama-backed reasoning and generation.', items: ['MKultra model', 'Model router', 'Prompt context', 'Local inference'] },
      { title: 'Local Knowledge and Memory', status: 'planned', detail: 'Member-controlled retrieval and persistence.', items: ['Qdrant vectors', 'SQLite metadata', 'Consent state', 'Selective mirroring'] },
      { title: 'Thin Line Lab', status: 'development', detail: 'Deterministic simulation and scientific tooling.', items: ['Simulation engine', 'Metric frames', 'Contradiction tests', 'Reproducible runs'] },
    ],
  },
  {
    title: '2. Identity and Trust Layer',
    boundary: 'Identity is cryptographic; authority is policy-derived',
    nodes: [
      { title: 'NodeID', status: 'implemented', detail: 'Public-key-derived node identifier.', items: ['nodeid:cv1 namespace', 'Ed25519-compatible records', 'Key lifecycle', 'Principal binding'] },
      { title: 'Authenticated Session', status: 'planned', detail: 'Gateway-verified principal and node session.', items: ['Session ID', 'Nonce', 'Clock-skew checks', 'Proof-of-possession'] },
      { title: 'Node Registry', status: 'planned', detail: 'Durable node and public-key registry.', items: ['Registration', 'Activation', 'Suspension', 'Revocation and rotation'] },
      { title: 'Authorization Policy', status: 'planned', detail: 'Server-side policy independent of resource metadata.', items: ['Namespace rules', 'Consent', 'Role checks', 'Scope decisions'] },
    ],
  },
  {
    title: '3. Civilisation.One Gateway Layer',
    boundary: 'Only authenticated, policy-checked operations cross this boundary',
    nodes: [
      { title: 'API Gateway', status: 'planned', detail: 'Single controlled entry point for member nodes.', items: ['TLS', 'Authentication', 'Rate limits', 'Payload limits'] },
      { title: 'Agent and Tool Router', status: 'development', detail: 'Routes requests to approved models, tools, and data.', items: ['LangGraph flows', 'Tool permissions', 'Context assembly', 'Failure isolation'] },
      { title: 'Consent and Governance', status: 'planned', detail: 'Applies member consent and organisation policy.', items: ['Policy versions', 'Withdrawal', 'Appeals', 'Administrative review'] },
      { title: 'Private MKone Boundary', status: 'blocked', detail: 'No direct browser or member-node access.', items: ['Gateway-only access', 'Explicit tool contracts', 'Audit trail', 'No implicit authority'] },
    ],
  },
  {
    title: '4. OIIIDS Resource Exchange Layer',
    boundary: 'Resources are immutable publications, not mutable authority records',
    nodes: [
      { title: 'Resource Envelope', status: 'implemented', detail: 'Canonical, versioned, digest-addressed resource.', items: ['Manifest', 'Payload', 'SHA-256 digest', 'Parent provenance'] },
      { title: 'Publication Service', status: 'implemented', detail: 'Development-stage publish/read/version operations.', items: ['Digest validation', 'Owner check', 'Signing interface', 'Observer boundary'] },
      { title: 'Process Engine', status: 'implemented', detail: 'Guarded process state model.', items: ['Authenticate', 'Verify node', 'Authorize', 'Validate and commit'] },
      { title: 'Offline Sync and CRDT', status: 'planned', detail: 'Convergent local editing and selective replication.', items: ['Automerge resources', 'Delta exchange', 'Conflict preservation', 'Semantic resolution'] },
    ],
  },
  {
    title: '5. Persistence and Evidence Layer',
    boundary: 'Operational data, audit evidence, and payload storage remain separated',
    nodes: [
      { title: 'Resource Store', status: 'development', detail: 'Currently in-memory; durable adapter required.', items: ['SQLite local', 'PostgreSQL shared', 'Atomic versions', 'Integrity scans'] },
      { title: 'Object Storage', status: 'planned', detail: 'Encrypted payload and evidence blobs.', items: ['Datasets', 'Images', 'Reports', 'Large model artifacts'] },
      { title: 'Transactional Outbox', status: 'planned', detail: 'Commits audit delivery with state changes.', items: ['Idempotency', 'Retry', 'Event ordering', 'Failure recovery'] },
      { title: 'Backup and Recovery', status: 'blocked', detail: 'Production gate remains closed until restore is tested.', items: ['Snapshots', 'Key registry backup', 'Digest recomputation', 'Disaster recovery drills'] },
    ],
  },
  {
    title: '6. Observer and Operations Layer',
    boundary: 'Telemetry observes health; it never grants authority',
    nodes: [
      { title: 'Observer Audit', status: 'development', detail: 'Integrity-oriented event sink boundary.', items: ['Publication events', 'Process transitions', 'Revocations', 'Incident evidence'] },
      { title: 'OpenTelemetry', status: 'planned', detail: 'Operational traces and metrics without private payloads.', items: ['Latency', 'Error rate', 'Queue depth', 'Correlation IDs'] },
      { title: 'Quarantine', status: 'planned', detail: 'Invalid or unverifiable resources are isolated.', items: ['Signature failures', 'Digest mismatch', 'Policy rejection', 'Manual review'] },
      { title: 'Operations Dashboard', status: 'implemented', detail: 'Repository implementation status, not live telemetry.', items: ['NodeID status', 'Process map', 'Safety gates', 'Production blockers'] },
    ],
  },
];

const flow = [
  'Member action',
  'Local validation',
  'Authenticated gateway',
  'NodeID proof verification',
  'Policy authorization',
  'OIIIDS process engine',
  'Canonical resource commit',
  'Observer audit event',
  'Selective distribution',
  'Local verification and use',
];

const SystemMap: React.FC = () => (
  <div className="p-6 md:p-8 max-w-[1600px] mx-auto space-y-6 overflow-y-auto h-full">
    <header className="flex flex-col xl:flex-row xl:items-end xl:justify-between gap-4">
      <div>
        <p className="text-[10px] uppercase tracking-[0.3em] text-cyan-400 font-bold">MirrorME × Civilisation.One</p>
        <h1 className="text-3xl font-black text-slate-100 mt-2">Full System Map</h1>
        <p className="text-sm text-slate-400 mt-2 max-w-4xl">
          End-to-end architecture from the member-controlled local node through identity, gateway policy, OIIIDS resource exchange,
          persistence, audit, synchronization, models, simulations, and operational controls.
        </p>
      </div>
      <div className="rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3">
        <div className="text-[9px] uppercase tracking-widest text-red-300 font-bold">Production Gate</div>
        <div className="text-lg font-black text-red-200">Closed</div>
        <div className="text-[10px] text-red-300/70">Architecture and development map</div>
      </div>
    </header>

    <section className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
      <h2 className="text-xs uppercase tracking-widest text-cyan-400 font-bold mb-4">Primary Operation Flow</h2>
      <div className="flex flex-wrap items-center gap-2">
        {flow.map((step, index) => (
          <React.Fragment key={step}>
            <div className="rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-xs text-slate-200">
              <span className="text-cyan-400 font-bold mr-2">{index + 1}</span>{step}
            </div>
            {index < flow.length - 1 && <span className="text-slate-600">→</span>}
          </React.Fragment>
        ))}
      </div>
    </section>

    <div className="space-y-5">
      {layers.map((layer) => (
        <section key={layer.title} className="rounded-2xl border border-slate-800 bg-slate-900/80 p-5">
          <div className="mb-4">
            <h2 className="text-base font-bold text-slate-100">{layer.title}</h2>
            <p className="text-xs text-slate-500 mt-1">Boundary: {layer.boundary}</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-3">
            {layer.nodes.map((node) => (
              <article key={node.title} className="rounded-xl border border-slate-800 bg-slate-950 p-4">
                <div className="flex items-start justify-between gap-2 mb-2">
                  <h3 className="text-sm font-bold text-slate-100">{node.title}</h3>
                  <span className={`text-[8px] uppercase tracking-wider border rounded-full px-2 py-1 ${statusStyle[node.status]}`}>
                    {node.status}
                  </span>
                </div>
                <p className="text-xs text-slate-400 mb-3">{node.detail}</p>
                <ul className="space-y-1.5">
                  {node.items.map((item) => <li key={item} className="text-[11px] text-slate-500 border-l border-slate-700 pl-2">{item}</li>)}
                </ul>
              </article>
            ))}
          </div>
        </section>
      ))}
    </div>

    <section className="grid grid-cols-1 lg:grid-cols-3 gap-4">
      <div className="rounded-xl border border-emerald-500/20 bg-emerald-500/5 p-4">
        <h3 className="text-xs uppercase tracking-widest text-emerald-300 font-bold">Implemented Core</h3>
        <p className="text-xs text-slate-400 mt-2">Dashboard, deterministic simulations, immutable resource envelopes, digest checks, development signer, NodeID models, and guarded process states.</p>
      </div>
      <div className="rounded-xl border border-amber-500/20 bg-amber-500/5 p-4">
        <h3 className="text-xs uppercase tracking-widest text-amber-300 font-bold">Next Engineering Gate</h3>
        <p className="text-xs text-slate-400 mt-2">Live Ed25519 verification, durable node registry, SQLite process repository, idempotency, transactional outbox, and authenticated API integration.</p>
      </div>
      <div className="rounded-xl border border-red-500/20 bg-red-500/5 p-4">
        <h3 className="text-xs uppercase tracking-widest text-red-300 font-bold">Production Blockers</h3>
        <p className="text-xs text-slate-400 mt-2">Protected key storage, encryption, rate limits, tested backups, disaster recovery, policy service, audit integrity, and end-to-end security validation.</p>
      </div>
    </section>
  </div>
);

export default SystemMap;
