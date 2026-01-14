
import React from 'react';
import Sidebar from './Sidebar';
import { SimulationState } from '../types';

interface LayoutProps {
  children: React.ReactNode;
  simState: SimulationState;
  toggleSimulation: () => void;
}

const Layout: React.FC<LayoutProps> = ({ children, simState, toggleSimulation }) => {
  return (
    <div className="flex h-screen w-full bg-slate-950 text-slate-200 overflow-hidden">
      <Sidebar />
      <main className="flex-1 flex flex-col min-w-0">
        <header className="h-14 border-b border-slate-800 flex items-center justify-between px-6 bg-slate-900/50 backdrop-blur-md">
          <div className="flex items-center gap-4">
            <h1 className="font-bold tracking-tight text-lg text-cyan-400">MirrorMe <span className="text-slate-500 font-normal">/</span> Project MKone</h1>
            <div className="h-4 w-[1px] bg-slate-700" />
            <div className="flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${simState.isRunning ? 'bg-green-500 animate-pulse' : 'bg-slate-600'}`} />
              <span className="text-xs uppercase font-medium tracking-widest text-slate-400">
                {simState.isRunning ? 'Live Engine Sync' : 'Engine Idle'}
              </span>
            </div>
          </div>
          
          <div className="flex items-center gap-4">
             <button 
              onClick={toggleSimulation}
              className={`px-4 py-1.5 rounded-full text-xs font-bold transition-all ${
                simState.isRunning 
                ? 'bg-red-500/10 text-red-500 border border-red-500/20 hover:bg-red-500/20' 
                : 'bg-cyan-500 text-slate-950 hover:bg-cyan-400'
              }`}
            >
              {simState.isRunning ? 'STOP SIMULATION' : 'START SIMULATION'}
            </button>
            <div className="text-xs mono text-slate-500 bg-slate-800/50 px-2 py-1 rounded">
              T+{simState.currentFrame.toString().padStart(6, '0')}
            </div>
          </div>
        </header>
        <div className="flex-1 relative overflow-auto">
          {children}
        </div>
      </main>
    </div>
  );
};

export default Layout;
