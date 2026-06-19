import React from 'react';

const Settings: React.FC = () => {
  return (
    <div className="p-8 max-w-4xl mx-auto">
      <h2 className="text-3xl font-bold text-slate-100 mb-2">Engine Configuration</h2>
      <p className="text-slate-400 mb-8">Static deployment settings for the MirrorMe / MKone browser console.</p>

      <div className="space-y-6">
        <section className="bg-slate-900 border border-slate-800 p-6 rounded-2xl">
          <h3 className="text-sm font-bold text-slate-500 uppercase tracking-widest mb-4">Neural Parameters</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <label className="text-xs font-medium text-slate-400">Gamma-Sync Display Target</label>
              <input type="range" defaultValue={42} min={30} max={60} className="w-full h-1 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-cyan-500" />
              <div className="flex justify-between text-[10px] text-slate-600 font-bold uppercase">
                <span>30 Hz</span>
                <span>60 Hz</span>
              </div>
            </div>
            <div className="space-y-2">
              <label className="text-xs font-medium text-slate-400">Psi-Snap Frequency (Hz)</label>
              <input type="number" defaultValue={60} className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-cyan-500" />
            </div>
          </div>
        </section>

        <section className="bg-slate-900 border border-slate-800 p-6 rounded-2xl">
          <h3 className="text-sm font-bold text-slate-500 uppercase tracking-widest mb-4">Runtime Layer</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 bg-slate-950 rounded-xl border border-slate-800">
               <div className="flex items-center gap-4">
                 <div className="w-10 h-10 rounded-lg bg-cyan-500/10 flex items-center justify-center text-cyan-500">
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" /></svg>
                 </div>
                 <div>
                   <h4 className="text-sm font-bold text-slate-200">Browser Simulator</h4>
                   <p className="text-xs text-slate-500">Client-side telemetry and 3D simulation. No backend required.</p>
                 </div>
               </div>
               <span className="px-2 py-1 bg-green-500/10 text-green-500 text-[10px] font-bold rounded border border-green-500/20">ACTIVE</span>
            </div>
            <div className="flex items-center justify-between p-4 bg-slate-950 rounded-xl border border-slate-800 opacity-75">
               <div className="flex items-center gap-4">
                 <div className="w-10 h-10 rounded-lg bg-indigo-500/10 flex items-center justify-center text-indigo-500">
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 1.105 2.239 2 5 2s5-.895 5-2V7M4 7c0 1.105 2.239 2 5 2s5-.895 5-2M4 7c0-1.105 2.239-2 5-2s5 .895 5 2" /></svg>
                 </div>
                 <div>
                   <h4 className="text-sm font-bold text-slate-200">Database / Flight Recorder</h4>
                   <p className="text-xs text-slate-500">Not connected in GitHub Pages static deployment.</p>
                 </div>
               </div>
               <span className="px-2 py-1 bg-slate-800 text-slate-500 text-[10px] font-bold rounded border border-slate-700 uppercase">Static Demo</span>
            </div>
            <div className="flex items-center justify-between p-4 bg-slate-950 rounded-xl border border-slate-800 opacity-75">
               <div className="flex items-center gap-4">
                 <div className="w-10 h-10 rounded-lg bg-orange-500/10 flex items-center justify-center text-orange-500">
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
                 </div>
                 <div>
                   <h4 className="text-sm font-bold text-slate-200">Remote AI Provider</h4>
                   <p className="text-xs text-slate-500">Optional. Offline fallback responds without secrets.</p>
                 </div>
               </div>
               <span className="px-2 py-1 bg-slate-800 text-slate-500 text-[10px] font-bold rounded border border-slate-700 uppercase">Optional</span>
            </div>
          </div>
        </section>

        <section className="bg-red-500/5 border border-red-500/20 p-6 rounded-2xl">
          <h3 className="text-sm font-bold text-red-400 uppercase tracking-widest mb-4">Safety Boundary</h3>
          <p className="text-xs text-slate-500 mb-4">This public deployment is a static browser console. It does not store private memory, credentials, or hidden telemetry.</p>
          <div className="flex gap-4">
             <button className="px-4 py-2 bg-red-500/10 text-red-500 border border-red-500/20 rounded-lg text-xs font-bold hover:bg-red-500/20 transition-all uppercase">
               Clear Local Simulation Cache
             </button>
             <button className="px-4 py-2 border border-slate-700 rounded-lg text-xs font-bold text-slate-400 hover:bg-slate-800 transition-all uppercase">
               Reset Workspace View
             </button>
          </div>
        </section>
      </div>
    </div>
  );
};

export default Settings;
