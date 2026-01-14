
import React, { useMemo } from "react";
import {
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  AreaChart, Area, LineChart, Line, ReferenceLine
} from "recharts";
import { SimulationState } from "../types";

const V_MIN = 0.99;
const EPS_MAX = 0.05;

// Convert canonical seconds to microseconds for display
const driftToUs = (driftSeconds: number) => driftSeconds * 1e6;

const Dashboard: React.FC<{ simState: SimulationState }> = ({ simState }) => {
  const currentMetric = useMemo(() => {
    return simState.metrics[simState.metrics.length - 1] ?? {
      gamma: 0, psi: 0, vireax: 0, error: 0, drift: 0, entropy: 0
    };
  }, [simState.metrics]);

  const data = useMemo(() => {
    return simState.metrics.map((m, idx) => ({
      ...m,
      // Map display-only derived fields to avoid mutating truth-layer
      gamma_display: Number(m.gamma.toFixed(2)),
      vireax_display: Number(m.vireax.toFixed(4)),
      error_display: Number(m.error.toFixed(4)),
      drift_us_display: Number(driftToUs(m.drift).toFixed(2)),
      timestamp: idx.toString()
    }));
  }, [simState.metrics]);

  return (
    <div className="p-4 flex flex-col gap-4 overflow-y-auto h-full scrollbar-hide">
      {/* Real-time Telemetry Tickers */}
      <div className="grid grid-cols-3 gap-2">
        <div className="bg-slate-900 border border-slate-800 p-3 rounded-xl shadow-sm border-t-2 border-t-cyan-500/30">
          <h4 className="text-[9px] text-slate-500 font-bold uppercase mb-1 tracking-wider">Stability (v)</h4>
          <p className={`text-lg font-bold mono ${currentMetric.vireax < V_MIN ? "text-red-400" : "text-cyan-400"}`}>
            {(currentMetric.vireax * 100).toFixed(2)}%
          </p>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-3 rounded-xl shadow-sm border-t-2 border-t-indigo-500/30">
          <h4 className="text-[9px] text-slate-500 font-bold uppercase mb-1 tracking-wider">Jitter (Δt)</h4>
          <p className="text-lg font-bold text-indigo-400 mono">
            {driftToUs(currentMetric.drift).toFixed(2)}μs
          </p>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-3 rounded-xl shadow-sm border-t-2 border-t-orange-500/30">
          <h4 className="text-[9px] text-slate-500 font-bold uppercase mb-1 tracking-wider">Reasoning (ε)</h4>
          <p className={`text-lg font-bold mono ${currentMetric.error > EPS_MAX ? "text-orange-400" : "text-slate-300"}`}>
            {(currentMetric.error * 100).toFixed(2)}%
          </p>
        </div>
      </div>

      {/* Stability Timeline (O(1) Chart Data via Ring Buffer) */}
      <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl flex-1 min-h-[180px]">
        <h4 className="text-[10px] text-slate-500 font-bold uppercase mb-4 tracking-widest flex justify-between">
          Cognitive Audit Trace
          <span className="text-[8px] text-slate-600">O(1) Ring Buffer</span>
        </h4>
        <div className="h-full w-full min-h-[140px]">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
              <XAxis dataKey="timestamp" hide />
              {/* Fixed Y domain for stability: 0.9 to 1.0 */}
              <YAxis domain={[0.9, 1.0]} hide />
              <Tooltip
                contentStyle={{ backgroundColor: "#0f172a", border: "1px solid #1e293b", fontSize: "10px" }}
                itemStyle={{ padding: 0 }}
              />
              {/* Reference Lines define the Truth Boundary */}
              <ReferenceLine y={V_MIN} stroke="#22d3ee" strokeDasharray="3 3" label={{ position: 'right', value: 'v_min', fill: '#22d3ee', fontSize: 8 }} />
              <ReferenceLine y={EPS_MAX} stroke="#ef4444" strokeDasharray="3 3" label={{ position: 'right', value: 'ε_max', fill: '#ef4444', fontSize: 8 }} />
              
              <Line type="monotone" dataKey="vireax_display" stroke="#22d3ee" strokeWidth={2} dot={false} isAnimationActive={false} name="Stability" />
              <Line type="monotone" dataKey="error_display" stroke="#ef4444" strokeWidth={1.5} strokeDasharray="4 4" dot={false} isAnimationActive={false} name="Error" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Sync Field (Gamma) */}
      <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl flex-1 min-h-[160px]">
        <h4 className="text-[10px] text-slate-500 font-bold uppercase mb-4 tracking-widest flex justify-between">
          Spectral Field (γ)
          <span className="text-cyan-500 font-mono text-[9px]">Calibrated @ 42Hz</span>
        </h4>
        <div className="h-full w-full min-h-[120px]">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data}>
              <defs>
                <linearGradient id="colorSync" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#818cf8" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#818cf8" stopOpacity={0} />
                </linearGradient>
              </defs>
              <XAxis dataKey="timestamp" hide />
              <YAxis domain={[30, 60]} hide />
              <Tooltip contentStyle={{ backgroundColor: "#0f172a", border: "1px solid #1e293b", fontSize: "10px" }} />
              <Area type="monotone" dataKey="gamma_display" stroke="#818cf8" fillOpacity={1} fill="url(#colorSync)" isAnimationActive={false} name="Gamma (Hz)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
