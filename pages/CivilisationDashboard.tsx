import React from 'react';

const CivilisationDashboard: React.FC = () => {
  const stats = [
    { label: 'Global Statistics', value: '74.2', sub: 'Composite resilience index' },
    { label: 'Education Metrics', value: '81.6', sub: 'Access and learning quality' },
    { label: 'Happiness/Safety', value: '68.9', sub: 'Wellbeing and risk profile' },
    { label: 'Research Progress', value: '59.4', sub: 'Breakthrough velocity' },
  ];

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="flex items-end justify-between gap-4">
        <div>
          <h2 className="text-3xl font-bold text-slate-100 mb-2">Civilisation Dashboard</h2>
          <p className="text-slate-400">Macro-state monitoring for collective progress and system health.</p>
        </div>
        <div className="px-5 py-3 rounded-xl border border-cyan-500/30 bg-cyan-500/10 text-cyan-300">
          <div className="text-[10px] uppercase tracking-widest font-bold">Civilisation Score</div>
          <div className="text-2xl font-black">71.0</div>
        </div>
      </div>

      <section className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
        {stats.map((item) => (
          <div key={item.label} className="p-5 rounded-2xl border border-slate-800 bg-slate-900">
            <div className="text-[10px] uppercase tracking-widest text-slate-500 font-bold mb-2">{item.label}</div>
            <div className="text-2xl font-black text-slate-100 mb-1">{item.value}</div>
            <div className="text-xs text-slate-400">{item.sub}</div>
          </div>
        ))}
      </section>

      <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
        <h3 className="text-xs uppercase tracking-widest text-cyan-400 font-bold mb-4">Infrastructure</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 rounded-xl border border-slate-800 bg-slate-950">
            <h4 className="text-sm font-bold text-slate-200 mb-1">DePIN Nodes</h4>
            <p className="text-sm text-slate-400">Distributed physical infrastructure nodes for resilient computation and sensing.</p>
          </div>
          <div className="p-4 rounded-xl border border-slate-800 bg-slate-950">
            <h4 className="text-sm font-bold text-slate-200 mb-1">QVIREAX Quantum Network Research</h4>
            <p className="text-sm text-slate-400">Experimental pathway for high-fidelity synchronization and secure distributed reasoning.</p>
          </div>
          <div className="p-4 rounded-xl border border-slate-800 bg-slate-950">
            <h4 className="text-sm font-bold text-slate-200 mb-1">Governance/Audit Layer</h4>
            <p className="text-sm text-slate-400">Policy, traceability, and accountability controls for system decisions.</p>
          </div>
          <div className="p-4 rounded-xl border border-slate-800 bg-slate-950">
            <h4 className="text-sm font-bold text-slate-200 mb-1">Token/Reward Systems</h4>
            <p className="text-sm text-slate-400">Incentive mechanics for contribution quality, transparency, and long-term alignment.</p>
          </div>
        </div>
      </section>
    </div>
  );
};

export default CivilisationDashboard;
