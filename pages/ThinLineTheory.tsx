import React from 'react';

const ThinLineTheory: React.FC = () => {
  return (
    <div className="p-8 max-w-6xl mx-auto space-y-6">
      <div>
        <h2 className="text-3xl font-bold text-slate-100 mb-2">Thin Line Theory</h2>
        <p className="text-slate-400">Research workspace for documents, equations, simulations, and validation status.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        <section className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
          <h3 className="text-xs uppercase tracking-widest text-amber-400 font-bold mb-3">Theory Documents</h3>
          <ul className="space-y-2 text-sm text-slate-300">
            <li className="p-2 rounded bg-slate-950 border border-slate-800">Foundational assumptions</li>
            <li className="p-2 rounded bg-slate-950 border border-slate-800">Revision log and rationale</li>
            <li className="p-2 rounded bg-slate-950 border border-slate-800">Cross-domain implications</li>
          </ul>
        </section>

        <section className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
          <h3 className="text-xs uppercase tracking-widest text-amber-400 font-bold mb-3">Equations</h3>
          <div className="space-y-2 text-sm text-slate-300">
            <div className="p-2 rounded bg-slate-950 border border-slate-800 font-mono">v &gt;= 0.99</div>
            <div className="p-2 rounded bg-slate-950 border border-slate-800 font-mono">drift &lt;= 0.00001 s</div>
            <div className="p-2 rounded bg-slate-950 border border-slate-800 font-mono">epsilon &lt;= 0.05</div>
          </div>
        </section>

        <section className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
          <h3 className="text-xs uppercase tracking-widest text-amber-400 font-bold mb-3">Simulations</h3>
          <p className="text-sm text-slate-400 mb-3">Run test environments and compare output against expected dynamics.</p>
          <div className="h-28 rounded-xl border border-slate-800 bg-gradient-to-r from-slate-950 via-slate-900 to-slate-950" />
        </section>

        <section className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
          <h3 className="text-xs uppercase tracking-widest text-amber-400 font-bold mb-3">Evidence Status</h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between p-2 rounded bg-slate-950 border border-slate-800"><span className="text-slate-400">Mathematical consistency</span><span className="text-emerald-400">Validated</span></div>
            <div className="flex justify-between p-2 rounded bg-slate-950 border border-slate-800"><span className="text-slate-400">Empirical reproducibility</span><span className="text-amber-400">In review</span></div>
            <div className="flex justify-between p-2 rounded bg-slate-950 border border-slate-800"><span className="text-slate-400">Field-scale proof</span><span className="text-rose-400">Speculative</span></div>
          </div>
        </section>
      </div>

      <section className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
        <h3 className="text-xs uppercase tracking-widest text-amber-400 font-bold mb-3">Speculative vs Validated Separation</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 rounded-xl border border-rose-500/30 bg-rose-500/5">
            <h4 className="text-rose-400 font-bold text-sm mb-2">Speculative Track</h4>
            <p className="text-sm text-slate-300">Hypotheses without sufficient empirical support remain isolated until evidence thresholds are met.</p>
          </div>
          <div className="p-4 rounded-xl border border-emerald-500/30 bg-emerald-500/5">
            <h4 className="text-emerald-400 font-bold text-sm mb-2">Validated Track</h4>
            <p className="text-sm text-slate-300">Claims with reproducible methods and independent confirmation are promoted to stable theory status.</p>
          </div>
        </div>
      </section>
    </div>
  );
};

export default ThinLineTheory;
