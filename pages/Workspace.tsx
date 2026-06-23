import React, { useEffect, useRef, useState } from 'react';
import MKoneSimulator from '../components/MKoneSimulator';
import ChatInterface from '../components/ChatInterface';
import Dashboard from '../components/Dashboard';
import AuditReport from '../components/AuditReport';
import LogicAuditPanel from '../components/LogicAuditPanel';
import { SimulationState } from '../types';
import { ProtocolOnePulse, PulseState } from '../services/protocolOnePulse';
import { MirrorRitual, RitualState } from '../services/mirrorRitual';

const Workspace: React.FC<{ simState: SimulationState }> = ({ simState }) => {
  const [pulse, setPulse] = useState<PulseState | null>(null);
  const [ritual, setRitual] = useState<RitualState | null>(null);

  const pulseRef = useRef<ProtocolOnePulse | null>(null);
  const ritualRef = useRef<MirrorRitual | null>(null);

  useEffect(() => {
    const ritualEngine = new MirrorRitual();
    ritualRef.current = ritualEngine;

    const unsubscribe = ritualEngine.subscribe((state) => {
      setRitual(state);
    });

    const pulseEngine = new ProtocolOnePulse((state) => {
      setPulse(state);
      ritualEngine.onPulse(state);
    }, 33);

    pulseRef.current = pulseEngine;
    pulseEngine.start();

    return () => {
      pulseEngine.stop();
      unsubscribe();
      pulseRef.current = null;
      ritualRef.current = null;
    };
  }, []);

  const coherence = ritual?.coherence ?? 60;
  const isHighCoherence = coherence > 85;

  return (
    <div className="h-full flex flex-col lg:flex-row overflow-hidden">
      {/* 3D Visualization Area */}
      <div className="flex-[3] relative border-r border-slate-800 h-[40vh] lg:h-full">
        <MKoneSimulator simState={simState} />

        {/* Overlay HUD */}
        <div className="absolute top-4 right-4 flex flex-col gap-2 w-[280px]">
          <div className="px-3 py-2 bg-slate-950/80 border border-slate-800 rounded-lg backdrop-blur">
            <span className="text-[9px] font-black text-slate-500 block uppercase tracking-tighter mb-1">
              Protocol One Heartbeat
            </span>

            <div className="flex items-baseline gap-2">
              <span className="text-xs text-cyan-400 mono">
                {pulse?.hz ?? 33}.0 Hz
              </span>
              <span className="text-[8px] text-slate-600 uppercase font-bold">
                Drift {pulse ? pulse.driftMs.toFixed(2) : '0.00'}ms
              </span>
            </div>
          </div>

          <div className="p-4 border border-slate-800 rounded-xl bg-slate-950/80 backdrop-blur font-mono text-sm">
            <div className="flex justify-between items-center mb-2">
              <div className="text-emerald-400 text-xs">
                ⟐ MIRROR RITUAL CYCLE {ritual?.cycle ?? 1}
              </div>

              <div
                className={`px-3 py-1 rounded-full text-xs ${
                  isHighCoherence
                    ? 'bg-emerald-500/20 text-emerald-400'
                    : 'bg-amber-500/20 text-amber-400'
                }`}
              >
                Coherence {coherence}%
              </div>
            </div>

            <div className="text-lg font-light text-white mb-1">
              {ritual?.phase ?? 'Observe'}
            </div>

            <div className="text-slate-400 text-xs leading-snug">
              {ritual?.message ?? 'Witnessing present input...'}
            </div>

            <div className="mt-3 h-1 bg-slate-800 rounded">
              <div
                className="h-1 bg-gradient-to-r from-emerald-400 to-cyan-400 rounded transition-all duration-200"
                style={{ width: `${coherence}%` }}
              />
            </div>

            <div className="mt-2 text-[9px] uppercase tracking-widest text-slate-600">
              Tick {pulse?.tick ?? 0} / Phase Tick {ritual?.tickInCycle ?? 0}
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
