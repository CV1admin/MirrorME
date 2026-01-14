
import React from 'react';

const Settings: React.FC = () => {
  return (
    <div className="p-8 max-w-4xl mx-auto">
      <h2 className="text-3xl font-bold text-slate-100 mb-2">Engine Configuration</h2>
      <p className="text-slate-400 mb-8">Adjust the MKone brain simulator parameters and system truth-layers.</p>

      <div className="space-y-6">
        <section className="bg-slate-900 border border-slate-800 p-6 rounded-2xl">
          <h3 className="text-sm font-bold text-slate-500 uppercase tracking-widest mb-4">Neural Parameters</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <label className="text-xs font-medium text-slate-400">Gamma-Sync Threshold</label>
              <input type="range" className="w-full h-1 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-cyan-500" />
              <div className="flex justify-between text-[10px] text-slate-600 font-bold uppercase">
                <span>Low Chaos</span>
                <span>High Coherence</span>
              </div>
            </div>
            <div className="space-y-2">
              <label className="text-xs font-medium text-slate-400">Psi-Snap Frequency (Hz)</label>
              <input type="number" defaultValue={60} className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-cyan-500" />
            </div>
          </div>
        </section>

        <section className="bg-slate-900 border border-slate-800 p-6 rounded-2xl">
          <h3 className="text-sm font-bold text-slate-500 uppercase tracking-widest mb-4">Storage Layer</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 bg-slate-950 rounded-xl border border-slate-800">
               <div className="flex items-center gap-4">
                 <div className="w-10 h-10 rounded-lg bg-indigo-500/10 flex items-center justify-center text-indigo-500">
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 1.105 2.239 2 5 2s5-.895 5-2V7M4 7c0 1.105 2.239 2 5 2s5-.895 5-2M4 7c0-1.105 2.239-2 5-2s5 .895 5 2m0 5c0 1.105-2.239 2-5 2s-5-.895-5-2" /></svg>
                 </div>
                 <div>
                   <h4 className="text-sm font-bold text-slate-200">Postgres Connector</h4>
                   <p className="text-xs text-slate-500">Truth-layer for relational cognitive artifacts.</p>
                 </div>
               </div>
               <span className="px-2 py-1 bg-green-500/10 text-green-500 text-[10px] font-bold rounded border border-green-500/20">CONNECTED</span>
            </div>
            <div className="flex items-center justify-between p-4 bg-slate-950 rounded-xl border border-slate-800 opacity-60">
               <div className="flex items-center gap-4">
                 <div className="w-10 h-10 rounded-lg bg-orange-500/10 flex items-center justify-center text-orange-500">
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" /></svg>
                 </div>
                 <div>
                   <h4 className="text-sm font-bold text-slate-200">S3 / MinIO Object Store</h4>
                   <p className="text-xs text-slate-500">Blob storage for frame arrays and videos.</p>
                 </div>
               </div>
               <span className="px-2 py-1 bg-slate-800 text-slate-500 text-[10px] font-bold rounded border border-slate-700 uppercase">Disabled</span>
            </div>
          </div>
        </section>

        <section className="bg-red-500/5 border border-red-500/20 p-6 rounded-2xl">
          <h3 className="text-sm font-bold text-red-400 uppercase tracking-widest mb-4">Danger Zone</h3>
          <p className="text-xs text-slate-500 mb-4">These actions are irreversible and will wipe truth-layer data.</p>
          <div className="flex gap-4">
             <button className="px-4 py-2 bg-red-500/10 text-red-500 border border-red-500/20 rounded-lg text-xs font-bold hover:bg-red-500/20 transition-all uppercase">
               Purge Simulation Cache
             </button>
             <button className="px-4 py-2 border border-slate-700 rounded-lg text-xs font-bold text-slate-400 hover:bg-slate-800 transition-all uppercase">
               Reset Workspace
             </button>
          </div>
        </section>
      </div>
    </div>
  );
};

export default Settings;
