
import React from 'react';
import MKoneSimulator from '../components/MKoneSimulator';
import ChatInterface from '../components/ChatInterface';
import Dashboard from '../components/Dashboard';
import AuditReport from '../components/AuditReport';
import LogicAuditPanel from '../components/LogicAuditPanel';
import { SimulationState } from '../types';

const Workspace: React.FC<{ simState: SimulationState }> = ({ simState }) => {
  return (
    <div className="h-full flex flex-col lg:flex-row overflow-hidden">
      {/* 3D Visualization Area */}
      <div className="flex-[3] relative border-r border-slate-800 h-[40vh] lg:h-full">
        <MKoneSimulator simState={simState} />
        
        {/* Overlay HUD */}
        <div className="absolute top-4 right-4 flex flex-col gap-2">
          <div className="px-3 py-2 bg-slate-950/80 border border-slate-800 rounded-lg backdrop-blur">
            <span className="text-[9px] font-black text-slate-500 block uppercase tracking-tighter mb-1">State Vector S(t)</span>
            <div className="flex items-baseline gap-2">
              <span className="text-xs text-cyan-400 mono">42.0 Hz</span>
              <span className="text-[8px] text-slate-600 uppercase font-bold">Standard Reference</span>
            </div>
          </div>
        </div>
      </div>

      {/* Control Plane: Dashboard & Logic Lab */}
      <div className="flex-[2] flex flex-col border-r border-slate-800 min-w-[340px] h-[30vh] lg:h-full bg-slate-950/20">
        <div className="flex-1 overflow-hidden border-b border-slate-800">
           <Dashboard simState={simState} />
        </div>
        <div className="h-[45%] shrink-0 flex flex-col">
          <LogicAuditPanel event={simState.activeContradiction} />
        </div>
      </div>

      {/* Right Sidebar: Audit & Chat */}
      <div className="flex-1 min-w-[320px] h-[30vh] lg:h-full flex flex-col bg-slate-950">
        <div className="h-1/3 border-b border-slate-800 overflow-hidden">
          <AuditReport simState={simState} />
        </div>
        <div className="flex-1 overflow-hidden">
          <ChatInterface simState={simState} />
        </div>
      </div>
    </div>
  );
};

export default Workspace;
