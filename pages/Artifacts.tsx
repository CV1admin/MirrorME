
import React from 'react';
import { Artifact } from '../types';

const Artifacts: React.FC = () => {
  const artifacts: Artifact[] = [
    { id: 'art-1', name: 'mk1_sim_run_001.jsonl', type: 'json', size: '2.4 MB', createdAt: '2024-05-20 14:22' },
    { id: 'art-2', name: 'neural_topology_export.mp4', type: 'mp4', size: '12.8 MB', createdAt: '2024-05-20 15:45' },
    { id: 'art-3', name: 'metric_history_v3.csv', type: 'csv', size: '840 KB', createdAt: '2024-05-21 09:12' },
    { id: 'art-4', name: 'snapshot_psi_delta.json', type: 'json', size: '1.2 MB', createdAt: '2024-05-21 10:30' },
  ];

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <div className="flex justify-between items-end mb-8">
        <div>
          <h2 className="text-3xl font-bold text-slate-100">Cognitive Artifacts</h2>
          <p className="text-slate-400">Historical traces and truth-layer exports from MKone runs.</p>
        </div>
        <button className="px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-sm font-medium hover:bg-slate-700 transition-colors">
          EXPORT ALL BUNDLE (.ZIP)
        </button>
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-2xl">
        <table className="w-full text-left">
          <thead className="bg-slate-950 border-b border-slate-800">
            <tr>
              <th className="px-6 py-4 text-xs font-bold uppercase text-slate-500 tracking-widest">Name</th>
              <th className="px-6 py-4 text-xs font-bold uppercase text-slate-500 tracking-widest">Type</th>
              <th className="px-6 py-4 text-xs font-bold uppercase text-slate-500 tracking-widest">Size</th>
              <th className="px-6 py-4 text-xs font-bold uppercase text-slate-500 tracking-widest">Created</th>
              <th className="px-6 py-4 text-xs font-bold uppercase text-slate-500 tracking-widest text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {artifacts.map((art) => (
              <tr key={art.id} className="hover:bg-slate-800/30 transition-colors group">
                <td className="px-6 py-4">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded bg-slate-800 flex items-center justify-center text-cyan-500">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" /></svg>
                    </div>
                    <span className="text-sm font-medium text-slate-200">{art.name}</span>
                  </div>
                </td>
                <td className="px-6 py-4">
                  <span className="px-2 py-0.5 rounded-full text-[10px] font-bold uppercase bg-slate-800 text-slate-400 border border-slate-700">
                    {art.type}
                  </span>
                </td>
                <td className="px-6 py-4 text-sm text-slate-400">{art.size}</td>
                <td className="px-6 py-4 text-sm text-slate-500 mono">{art.createdAt}</td>
                <td className="px-6 py-4 text-right">
                   <button className="text-cyan-500 hover:text-cyan-400 text-xs font-bold uppercase tracking-wider opacity-0 group-hover:opacity-100 transition-opacity">
                     Download
                   </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="mt-12 p-8 bg-gradient-to-br from-indigo-900/20 to-slate-900/40 rounded-3xl border border-indigo-500/20 relative overflow-hidden">
        <div className="relative z-10 max-w-lg">
          <h3 className="text-xl font-bold text-indigo-300 mb-2">Traceable Cognition Logs</h3>
          <p className="text-slate-400 text-sm mb-6">Every simulation run produces a comprehensive storyboard report. Share these artifacts with your team for collaborative audit-trails.</p>
          <button className="px-6 py-2.5 bg-indigo-500 text-slate-50 rounded-full text-sm font-bold shadow-lg shadow-indigo-500/20 hover:bg-indigo-400 transition-all">
            GENERATE TRACE REPORT
          </button>
        </div>
        <div className="absolute -right-20 -bottom-20 w-64 h-64 bg-indigo-500/10 rounded-full blur-3xl" />
      </div>
    </div>
  );
};

export default Artifacts;
