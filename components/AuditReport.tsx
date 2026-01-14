
import React from 'react';
import { SimulationState, GateStatus } from '../types';

const AuditReport: React.FC<{ simState: SimulationState }> = ({ simState }) => {
  const current = simState.metrics[simState.metrics.length - 1];
  
  const invariantChecks = [
    { name: 'Non-Contradiction', status: current && current.error < 0.08 ? 'PASS' : 'WARN' },
    { name: 'Temporal Causality', status: current && current.drift < 0.01 ? 'PASS' : 'FAIL' },
    { name: 'Memory Discipline', status: 'PASS' },
    { name: 'Tool Integrity', status: 'PASS' }
  ];

  return (
    <div className="h-full p-4 flex flex-col bg-slate-900/40 border-l border-slate-800 backdrop-blur-sm overflow-hidden">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xs font-black uppercase tracking-[0.2em] text-slate-400">MKone Gate Audit</h3>
        <div className={`px-2 py-0.5 rounded text-[10px] font-bold ${simState.gateStatus === GateStatus.GO ? 'text-green-400' : 'text-yellow-400'}`}>
          {simState.gateStatus}
        </div>
      </div>

      <div className="space-y-4 flex-1">
        <section>
          <h4 className="text-[9px] uppercase font-bold text-slate-600 mb-2">Invariant Validation</h4>
          <div className="space-y-2">
            {invariantChecks.map(check => (
              <div key={check.name} className="flex items-center justify-between bg-slate-950/50 p-2 rounded border border-slate-800/50">
                <span className="text-[10px] text-slate-300">{check.name}</span>
                <span className={`text-[9px] font-black px-1.5 py-0.5 rounded ${
                  check.status === 'PASS' ? 'text-green-500 bg-green-500/10' : 
                  check.status === 'WARN' ? 'text-yellow-500 bg-yellow-500/10' : 
                  'text-red-500 bg-red-500/10'
                }`}>
                  {check.status}
                </span>
              </div>
            ))}
          </div>
        </section>

        <section className="bg-slate-950/80 p-3 rounded-lg border border-slate-800">
           <h4 className="text-[9px] uppercase font-bold text-slate-600 mb-3">Decision Logic</h4>
           <div className="space-y-3">
             <div className="flex flex-col gap-1">
               <div className="flex justify-between text-[10px]">
                 <span className="text-slate-500">Go Confirmation</span>
                 <span className="text-slate-300 mono">{simState.consecutiveGoFrames}/5</span>
               </div>
               <div className="w-full h-1 bg-slate-800 rounded-full">
                 <div className="h-full bg-cyan-500 transition-all" style={{ width: `${(simState.consecutiveGoFrames / 5) * 100}%` }} />
               </div>
             </div>
             <div className="flex flex-col gap-1">
               <div className="flex justify-between text-[10px]">
                 <span className="text-slate-500">No-Go Pressure</span>
                 <span className="text-slate-300 mono">{simState.consecutiveNoGoFrames}/2</span>
               </div>
               <div className="w-full h-1 bg-slate-800 rounded-full">
                 <div className="h-full bg-red-500 transition-all" style={{ width: `${(simState.consecutiveNoGoFrames / 2) * 100}%` }} />
               </div>
             </div>
           </div>
        </section>
      </div>

      <div className="mt-auto pt-4">
        <div className="p-3 bg-indigo-500/5 border border-indigo-500/20 rounded-lg">
          <p className="text-[9px] text-indigo-300 leading-relaxed italic">
            "Every run is a cognitive artifact. If sync breaks, momentum must be sacrificed for correctness."
          </p>
        </div>
      </div>
    </div>
  );
};

export default AuditReport;
