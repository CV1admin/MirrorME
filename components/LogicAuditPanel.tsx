
import React from 'react';
import { ContradictionEvent } from '../types';

interface LogicAuditPanelProps {
  event?: ContradictionEvent;
}

const LogicAuditPanel: React.FC<LogicAuditPanelProps> = ({ event }) => {
  if (!event) {
    return (
      <div className="h-full flex flex-col items-center justify-center bg-slate-900/40 p-6 text-center">
        <div className="w-12 h-12 rounded-full border-2 border-dashed border-slate-700 mb-4 flex items-center justify-center opacity-40">
           <svg className="w-6 h-6 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
        </div>
        <h4 className="text-xs font-bold text-slate-500 uppercase tracking-widest">Logic Engine Standby</h4>
        <p className="text-[10px] text-slate-600 mt-2">No contradiction traps detected in active stream.</p>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col bg-slate-900 overflow-hidden border-t border-slate-800">
      <div className="p-3 bg-slate-950/50 border-b border-slate-800 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-rose-500 animate-ping" />
          <h3 className="text-[10px] font-black uppercase tracking-[0.2em] text-rose-400">Logic Audit Trace</h3>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-[9px] font-bold text-slate-500 mono">CONFIDENCE: {(event.confidence * 100).toFixed(0)}%</span>
          <span className="text-[9px] mono text-slate-600">ID: {event.id}</span>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-5 scrollbar-hide">
        {/* Conflict Inputs & Formalization */}
        <div className="space-y-2">
          <h4 className="text-[9px] uppercase font-bold text-slate-600 tracking-tighter">I/O Formalization Matrix</h4>
          <div className="grid grid-cols-1 gap-2">
            {Object.keys(event.inputs).map((key) => (
              <div key={key} className="bg-slate-950 p-3 rounded border border-slate-800 flex gap-4">
                <div className="w-6 h-6 rounded bg-slate-800 flex items-center justify-center text-[10px] font-black text-cyan-500 border border-slate-700">
                  {key}
                </div>
                <div className="flex-1">
                  <p className="text-xs text-slate-200 mb-1">{event.inputs[key]}</p>
                  <p className="text-[10px] mono text-slate-500 bg-slate-900/50 p-1 rounded">
                    {event.formalization[key]}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Auditor Findings */}
        <div className="bg-rose-500/5 p-4 rounded-xl border border-rose-500/20 relative overflow-hidden">
          <div className="absolute top-0 right-0 p-1 opacity-10">
            <svg className="w-12 h-12 text-rose-500" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" /></svg>
          </div>
          <h4 className="text-[9px] uppercase font-bold text-rose-400 mb-2">Audit Verdict</h4>
          <p className="text-xs font-black text-slate-100 mb-1">{event.result.classification}</p>
          <p className="text-[10px] text-slate-400 leading-tight italic">{event.result.explanation}</p>
          
          {event.violations.length > 0 && (
            <div className="mt-3 p-2 bg-slate-950/50 border border-rose-500/10 rounded">
               <span className="text-[8px] font-bold text-rose-500 uppercase block mb-1">Violations:</span>
               {event.violations.map((v, i) => (
                 <p key={i} className="text-[9px] text-slate-300 mono leading-tight">• {v}</p>
               ))}
            </div>
          )}
        </div>

        {/* Verification Metadata */}
        <div className="grid grid-cols-2 gap-3">
          <div className="space-y-2">
            <h4 className="text-[9px] uppercase font-bold text-slate-600">Assumptions</h4>
            <div className="bg-slate-950/50 p-2 rounded border border-slate-800">
              {event.assumptions.map((a, i) => (
                <p key={i} className="text-[9px] text-slate-400 mono leading-tight">• {a}</p>
              ))}
            </div>
          </div>
          <div className="space-y-2">
            <h4 className="text-[9px] uppercase font-bold text-slate-600">Constraints</h4>
            <div className="bg-slate-950/50 p-2 rounded border border-slate-800">
              {event.constraints_checked.map((c, i) => (
                <p key={i} className="text-[9px] text-slate-400 mono leading-tight">✓ {c}</p>
              ))}
            </div>
          </div>
        </div>

        {/* Repair Candidates */}
        <div className="space-y-2 pb-2">
          <h4 className="text-[9px] uppercase font-bold text-slate-600">Minimal-Change Repair Candidates</h4>
          {event.repairs_minimal.map((repair, i) => (
            <div key={i} className="bg-slate-950/50 p-3 rounded-lg border border-slate-800 flex flex-col gap-1 hover:border-indigo-500/50 transition-all group cursor-pointer">
              <div className="flex justify-between items-center">
                <span className="text-[10px] font-black text-indigo-400 uppercase tracking-tighter">{repair.type}</span>
                <span className={`text-[8px] font-black uppercase px-1.5 rounded ${
                  repair.cost === 'low' ? 'bg-green-500/10 text-green-500' : 
                  repair.cost === 'medium' ? 'bg-yellow-500/10 text-yellow-500' : 
                  'bg-rose-500/10 text-rose-500'
                }`}>
                  {repair.cost} COST
                </span>
              </div>
              <p className="text-xs text-slate-200 font-medium">{repair.change}</p>
              <p className="text-[9px] text-slate-500 leading-tight">{repair.notes}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="p-3 bg-slate-950 border-t border-slate-800 flex justify-between items-center gap-3">
        <button className="text-[9px] font-bold uppercase text-slate-600 hover:text-slate-400 transition-colors py-1">Dismiss Trap</button>
        <div className="flex gap-2">
          <button className="px-3 py-1.5 border border-slate-700 hover:bg-slate-800 text-slate-400 rounded text-[9px] font-black uppercase tracking-widest transition-all">
            FORK HYPOTHESIS
          </button>
          <button className="px-4 py-1.5 bg-indigo-600 text-slate-50 rounded text-[9px] font-black uppercase tracking-widest hover:bg-indigo-500 transition-all shadow-lg shadow-indigo-600/20 active:scale-95">
            COMMIT REPAIR
          </button>
        </div>
      </div>
    </div>
  );
};

export default LogicAuditPanel;
