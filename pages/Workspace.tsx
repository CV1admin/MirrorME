
import React from 'react';
import MKoneSimulator from '../components/MKoneSimulator';
import ChatInterface from '../components/ChatInterface';
import Dashboard from '../components/Dashboard';
import { SimulationState } from '../types';

const Workspace: React.FC<{ simState: SimulationState }> = ({ simState }) => {
  return (
    <div className="h-full flex flex-col md:flex-row overflow-hidden">
      {/* 3D Visualization Area */}
      <div className="flex-[2] relative border-r border-slate-800 h-[50vh] md:h-full">
        <MKoneSimulator simState={simState} />
        
        {/* Overlay Labels */}
        <div className="absolute top-4 right-4 pointer-events-none text-right">
          <div className="px-3 py-1 bg-slate-950/80 border border-slate-800 rounded mb-2">
            <span className="text-[10px] font-bold text-slate-500 block uppercase">Simulator Mode</span>
            <span className="text-xs text-slate-200">Neural-Net Topology V3</span>
          </div>
          <div className="px-3 py-1 bg-slate-950/80 border border-slate-800 rounded">
            <span className="text-[10px] font-bold text-slate-500 block uppercase">Orchestrator</span>
            <span className="text-xs text-cyan-400">Gemini-Engine-3</span>
          </div>
        </div>
      </div>

      {/* Dashboard & Chat Area */}
      <div className="flex-1 flex flex-col min-w-[380px] h-[50vh] md:h-full">
        <div className="flex-1 h-1/2 overflow-hidden border-b border-slate-800">
           <Dashboard simState={simState} />
        </div>
        <div className="flex-1 h-1/2 overflow-hidden">
          <ChatInterface />
        </div>
      </div>
    </div>
  );
};

export default Workspace;
