import React from 'react';
import type { QuantumNodeData } from './QuantumNodes';
import { calculateQuantumHealth, CIV1_QUANTUM_WEIGHT } from '../../lib/civScore';

interface QuantumDashboardProps {
  node: QuantumNodeData | null;
  onClose: () => void;
}

const QuantumDashboard: React.FC<QuantumDashboardProps> = ({ node, onClose }) => {
  if (!node) return null;

  const health = calculateQuantumHealth(node);
  const weightedContribution = health * CIV1_QUANTUM_WEIGHT;
  const coherencePct = Math.round(node.metrics.coherence * 100);

  return (
    <aside className="fixed right-4 top-20 z-50 w-80 rounded-2xl border border-cyan-400/50 bg-zinc-950/95 p-6 text-white shadow-2xl shadow-cyan-500/20 backdrop-blur-xl transition-transform duration-200 md:right-6 md:top-24 md:w-96">
      <div className="mb-6 flex items-start justify-between gap-4">
        <div>
          <h2 className="font-mono text-2xl text-cyan-300">{node.label}</h2>
          <p className="mt-1 text-emerald-400">
            CIV1-Q Score: <span className="text-3xl font-black">{node.score}</span>
          </p>
        </div>
        <button
          type="button"
          onClick={onClose}
          className="rounded-full px-2 text-2xl text-slate-400 hover:bg-slate-800 hover:text-white"
          aria-label="Close quantum node dashboard"
        >
          ×
        </button>
      </div>

      <div className="space-y-6">
        <div className="grid grid-cols-2 gap-4">
          <div className="rounded-xl bg-zinc-900 p-4">
            <div className="text-xs text-slate-400">COHERENCE</div>
            <div className="mt-1 font-mono text-4xl text-white">{coherencePct}%</div>
          </div>
          <div className="rounded-xl bg-zinc-900 p-4">
            <div className="text-xs text-slate-400">SPECTRAL DIM</div>
            <div className="mt-1 font-mono text-4xl text-white">{node.metrics.spectralDim.toFixed(2)}</div>
          </div>
        </div>

        <div>
          <div className="mb-2 text-xs text-slate-400">FINAL STATE</div>
          <div className="rounded-xl border border-cyan-400/20 bg-black p-4 font-mono text-2xl">
            {node.metrics.finalState}
          </div>
        </div>

        <div className="grid grid-cols-2 gap-3 text-xs">
          <div className="rounded-xl border border-slate-800 bg-slate-950 p-3">
            <div className="text-slate-500">Samples</div>
            <div className="mt-1 font-mono text-lg text-slate-100">{node.metrics.count ?? 'n/a'}</div>
          </div>
          <div className="rounded-xl border border-slate-800 bg-slate-950 p-3">
            <div className="text-slate-500">Health</div>
            <div className="mt-1 font-mono text-lg text-emerald-300">{Math.round(health * 100)}%</div>
          </div>
        </div>

        <div className="border-t border-cyan-400/20 pt-4 text-xs text-slate-400">
          <div>Lat: {node.lat.toFixed(3)}° | Lng: {node.lng.toFixed(3)}°</div>
          <div className="mt-2">
            Weighted CIV1 quantum pillar contribution:{' '}
            <span className="text-cyan-300">{(weightedContribution * 100).toFixed(1)}%</span>
          </div>
          <div className="mt-2 text-[10px] uppercase tracking-widest text-slate-600">
            Cluster coordinate. Not an exact personal or private device location.
          </div>
        </div>
      </div>
    </aside>
  );
};

export default QuantumDashboard;
