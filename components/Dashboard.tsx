
import React from 'react';
import { 
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area, LineChart, Line 
} from 'recharts';
import { SimulationState } from '../types';

const Dashboard: React.FC<{ simState: SimulationState }> = ({ simState }) => {
  const currentMetric = simState.metrics[simState.metrics.length - 1] || {
    gamma: 0, psi: 0, vireax: 0, error: 0, drift: 0, entropy: 0
  };

  const data = simState.metrics.map(m => ({
    ...m,
    gamma: parseFloat(m.gamma.toFixed(2)),
    vireax: parseFloat(m.vireax.toFixed(4)),
    error: parseFloat(m.error.toFixed(4)),
    drift: parseFloat((m.drift * 1000).toFixed(4)) // Display in microseconds
  }));

  return (
    <div className="p-4 flex flex-col gap-4 overflow-y-auto h-full scrollbar-hide">
      {/* Real-time Tickers */}
      <div className="grid grid-cols-3 gap-2">
        <div className="bg-slate-900 border border-slate-800 p-3 rounded-xl">
          <h4 className="text-[9px] text-slate-500 font-bold uppercase mb-1">Stability (v)</h4>
          <p className={`text-lg font-bold mono ${currentMetric.vireax < 0.99 ? 'text-red-400' : 'text-cyan-400'}`}>
            {(currentMetric.vireax * 100).toFixed(2)}%
          </p>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-3 rounded-xl">
          <h4 className="text-[9px] text-slate-500 font-bold uppercase mb-1">Drift (Δt)</h4>
          <p className="text-lg font-bold text-indigo-400 mono">
            {(currentMetric.drift * 1000).toFixed(2)}μs
          </p>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-3 rounded-xl">
          <h4 className="text-[9px] text-slate-500 font-bold uppercase mb-1">Error Proxy (ε)</h4>
          <p className={`text-lg font-bold mono ${currentMetric.error > 0.05 ? 'text-orange-400' : 'text-slate-300'}`}>
            {(currentMetric.error * 100).toFixed(2)}%
          </p>
        </div>
      </div>

      {/* Stability Timeline */}
      <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl flex-1 min-h-[160px]">
        <h4 className="text-[10px] text-slate-500 font-bold uppercase mb-4 tracking-widest">Cognitive Stability Trace (v/ε)</h4>
        <div className="h-full w-full min-h-[120px]">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
              <XAxis dataKey="timestamp" hide />
              <YAxis domain={['auto', 'auto']} hide />
              <Tooltip 
                contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #1e293b', fontSize: '10px' }}
              />
              <Line type="monotone" dataKey="vireax" stroke="#22d3ee" strokeWidth={2} dot={false} isAnimationActive={false} />
              <Line type="monotone" dataKey="error" stroke="#ef4444" strokeWidth={1.5} strokeDasharray="4 4" dot={false} isAnimationActive={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Sync Wave */}
      <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl flex-1 min-h-[160px]">
        <h4 className="text-[10px] text-slate-500 font-bold uppercase mb-4 tracking-widest">Spectral Sync (γ)</h4>
        <div className="h-full w-full min-h-[120px]">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data}>
              <defs>
                <linearGradient id="colorSync" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#818cf8" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#818cf8" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <XAxis dataKey="timestamp" hide />
              <YAxis domain={[30, 60]} hide />
              <Area type="monotone" dataKey="gamma" stroke="#818cf8" fillOpacity={1} fill="url(#colorSync)" isAnimationActive={false} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
