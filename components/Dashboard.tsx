
import React from 'react';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area 
} from 'recharts';
import { SimulationState } from '../types';

const Dashboard: React.FC<{ simState: SimulationState }> = ({ simState }) => {
  const currentMetric = simState.metrics[simState.metrics.length - 1] || {
    gamma: 0, psi: 0, error: 0, phi: 0, omega: 0
  };

  const data = simState.metrics.map(m => ({
    ...m,
    gamma: parseFloat(m.gamma.toFixed(4)),
    psi: parseFloat(m.psi.toFixed(4)),
    error: parseFloat(m.error.toFixed(4))
  }));

  return (
    <div className="p-4 flex flex-col gap-4 overflow-y-auto">
      {/* Real-time Tickers */}
      <div className="grid grid-cols-2 gap-3">
        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
          <h4 className="text-[10px] text-slate-500 font-bold uppercase mb-1">γ-Sync Velocity</h4>
          <p className="text-2xl font-bold text-cyan-400 mono">{currentMetric.gamma.toFixed(3)}</p>
          <div className="mt-2 h-1 w-full bg-slate-800 rounded-full overflow-hidden">
            <div className="h-full bg-cyan-400 transition-all duration-300" style={{ width: `${currentMetric.gamma * 100}%` }} />
          </div>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
          <h4 className="text-[10px] text-slate-500 font-bold uppercase mb-1">ψ-Snap Integral</h4>
          <p className="text-2xl font-bold text-indigo-400 mono">{currentMetric.psi.toFixed(3)}</p>
          <div className="mt-2 h-1 w-full bg-slate-800 rounded-full overflow-hidden">
            <div className="h-full bg-indigo-400 transition-all duration-300" style={{ width: `${currentMetric.psi * 100}%` }} />
          </div>
        </div>
      </div>

      {/* Main Charts */}
      <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl flex-1 min-h-[250px]">
        <h4 className="text-[10px] text-slate-500 font-bold uppercase mb-4">Neural Synchronization Timeline</h4>
        <div className="h-full w-full min-h-[180px]">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data}>
              <defs>
                <linearGradient id="colorGamma" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#22d3ee" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#22d3ee" stopOpacity={0}/>
                </linearGradient>
                <linearGradient id="colorPsi" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#818cf8" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#818cf8" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="timestamp" hide />
              <YAxis domain={[0, 1]} hide />
              <Tooltip 
                contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', color: '#f8fafc' }}
                itemStyle={{ color: '#22d3ee' }}
              />
              <Area type="monotone" dataKey="gamma" stroke="#22d3ee" fillOpacity={1} fill="url(#colorGamma)" isAnimationActive={false} />
              <Area type="monotone" dataKey="psi" stroke="#818cf8" fillOpacity={1} fill="url(#colorPsi)" isAnimationActive={false} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
         <h4 className="text-[10px] text-slate-500 font-bold uppercase mb-3">Placeholder Metaphysics</h4>
         <div className="space-y-3">
           <div className="flex items-center justify-between text-xs">
             <span className="text-slate-500">Φ (Phi)</span>
             <span className="mono text-slate-300">{currentMetric.phi.toFixed(2)} rad</span>
           </div>
           <div className="flex items-center justify-between text-xs">
             <span className="text-slate-500">Ω (Omega)</span>
             <span className="mono text-slate-300">{currentMetric.omega.toFixed(2)} ms</span>
           </div>
           <div className="flex items-center justify-between text-xs">
             <span className="text-slate-500">Δ (Delta)</span>
             <span className="mono text-green-400">READY</span>
           </div>
           <div className="flex items-center justify-between text-xs">
             <span className="text-slate-500">Simulation Error</span>
             <span className="mono text-rose-400">{(currentMetric.error * 100).toFixed(2)}%</span>
           </div>
         </div>
      </div>
    </div>
  );
};

export default Dashboard;
