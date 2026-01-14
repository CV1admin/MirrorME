
import React, { useState, useEffect, useCallback } from 'react';
import { HashRouter, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import Workspace from './pages/Workspace';
import Settings from './pages/Settings';
import Artifacts from './pages/Artifacts';
import { SimulationState, MetricFrame, BrainNode, GateStatus, ContradictionEvent } from './types';

const INITIAL_NODES: BrainNode[] = Array.from({ length: 40 }).map((_, i) => ({
  id: `node-${i}`,
  position: [
    (Math.random() - 0.5) * 10,
    (Math.random() - 0.5) * 10,
    (Math.random() - 0.5) * 10,
  ],
  activity: 0,
  type: i % 3 === 0 ? 'cognitive' : i % 3 === 1 ? 'sensory' : 'motor',
}));

const MOCK_CONTRADICTION: ContradictionEvent = {
  id: 'trap-resolution-swan-001',
  event: "contradiction_trap_resolution",
  timestamp: 0,
  inputs: {
    "A": "All swans are white.",
    "B": "A black swan exists."
  },
  formalization: {
    "A": "forall x (Swan(x) -> White(x))",
    "B": "exists x (Swan(x) and not White(x))"
  },
  result: {
    "classification": "INCONSISTENT_UNDER_CLASSICAL_LOGIC",
    "explanation": "B provides a counterexample to A."
  },
  repairs_minimal: [
    { type: "revise_axiom", change: "A -> 'Most swans are white'", cost: "low", notes: "Preserves classical logic." },
    { type: "defeasible_default", change: "A becomes a default rule", cost: "medium", notes: "Non-monotonic logic." },
    { type: "paraconsistent_logic", change: "Keep A and B; prevent explosion", cost: "medium-high", notes: "Logic layer upgrade." }
  ],
  assumptions: ["Classical FOL"],
  constraints_checked: ["Non-contradiction", "Minimal-change repairs"],
  violations: ["Non-contradiction violated"],
  confidence: 1.0,
  refs: ["MKone_LogicGate_Audit/ContradictionTrap"]
};

const App: React.FC = () => {
  const [simState, setSimState] = useState<SimulationState>({
    isRunning: false,
    gateStatus: GateStatus.NOGO,
    consecutiveGoFrames: 0,
    consecutiveNoGoFrames: 0,
    currentFrame: 0,
    metrics: [],
    nodes: INITIAL_NODES,
  });

  const updateSim = useCallback(() => {
    if (!simState.isRunning) return;

    setSimState((prev) => {
      const t = prev.currentFrame;
      
      const gamma = 40 + 5 * Math.sin(t * 0.05) + (Math.random() * 2);
      const psi = Math.max(0.99, 1 - (0.01 * Math.random()));
      const vireax = 0.994 + 0.005 * Math.sin(t * 0.02);
      
      // Drift in seconds (canonical). 0.00001s = 10us
      const drift = 0.000005 + (Math.random() * 0.000005);
      
      const error = (drift * 500) + (Math.random() * 0.02);
      const entropy = 0.4 + 0.1 * Math.cos(t * 0.03);

      const newFrame: MetricFrame = {
        timestamp: t,
        gamma,
        psi,
        vireax,
        drift,
        error,
        entropy,
      };

      let activeContradiction = prev.activeContradiction;
      if (t > 0 && t % 300 === 0 && !activeContradiction) {
        activeContradiction = { ...MOCK_CONTRADICTION, timestamp: t };
      } else if (t % 500 === 0) {
        activeContradiction = undefined; 
      }

      const isHealthy = vireax >= 0.99 && drift <= 0.00001 && error <= 0.05;

      let nextGate = prev.gateStatus;
      let nextGoFrames = prev.consecutiveGoFrames;
      let nextNoGoFrames = prev.consecutiveNoGoFrames;

      if (isHealthy) {
        nextGoFrames++;
        nextNoGoFrames = 0;
        if (nextGoFrames >= 5) nextGate = GateStatus.GO;
      } else {
        nextNoGoFrames++;
        nextGoFrames = 0;
        if (nextNoGoFrames >= 2) nextGate = GateStatus.NOGO;
        else if (nextGate === GateStatus.GO) nextGate = GateStatus.STABILIZING;
      }

      return {
        ...prev,
        gateStatus: nextGate,
        consecutiveGoFrames: nextGoFrames,
        consecutiveNoGoFrames: nextNoGoFrames,
        currentFrame: t + 1,
        // Ring buffer: keep last 100 points to ensure O(1) render time
        metrics: [...prev.metrics.slice(-99), newFrame],
        activeContradiction
      };
    });
  }, [simState.isRunning]);

  useEffect(() => {
    const interval = setInterval(updateSim, 50);
    return () => clearInterval(interval);
  }, [updateSim]);

  const toggleSimulation = () => {
    setSimState(prev => ({ 
      ...prev, 
      isRunning: !prev.isRunning,
      gateStatus: prev.isRunning ? GateStatus.NOGO : GateStatus.STABILIZING,
      consecutiveGoFrames: 0,
      consecutiveNoGoFrames: 0,
      activeContradiction: undefined
    }));
  };

  return (
    <HashRouter>
      <Layout simState={simState} toggleSimulation={toggleSimulation}>
        <Routes>
          <Route path="/" element={<Navigate to="/workspace" replace />} />
          <Route path="/workspace" element={<Workspace simState={simState} />} />
          <Route path="/artifacts" element={<Artifacts />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </Layout>
    </HashRouter>
  );
};

export default App;
