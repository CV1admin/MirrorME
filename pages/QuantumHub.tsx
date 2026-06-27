import React from 'react';
import QuantumHubSphere from '../components/sphere/QuantumHubSphere';

const QuantumHub: React.FC = () => {
  return (
    <div className="mx-auto max-w-7xl space-y-6 p-8">
      <div className="flex items-end justify-between gap-4">
        <div>
          <h2 className="mb-2 text-3xl font-bold text-slate-100">Quantum Hub</h2>
          <p className="text-slate-400">
            Interactive Civilisation.One research sphere for QRC and quantum-simulation cluster telemetry.
          </p>
        </div>
        <div className="rounded-xl border border-cyan-500/30 bg-cyan-500/10 px-5 py-3 text-cyan-300">
          <div className="text-[10px] font-bold uppercase tracking-widest">Mode</div>
          <div className="text-sm font-black leading-tight">Research Cluster View</div>
        </div>
      </div>

      <QuantumHubSphere />

      <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
        <h3 className="mb-4 text-xs font-bold uppercase tracking-widest text-cyan-400">Boundary</h3>
        <p className="text-sm text-slate-400">
          The displayed quantum nodes are visualization anchors for research clusters and simulated telemetry. They do not prove
          physical quantum networking, biological measurement, private device location, or live hardware attestation.
        </p>
      </section>
    </div>
  );
};

export default QuantumHub;
