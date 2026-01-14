
import React, { useState, useEffect, useCallback } from 'react';
import { HashRouter, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import Workspace from './pages/Workspace';
import Settings from './pages/Settings';
import Artifacts from './pages/Artifacts';
import { SimulationState, MetricFrame, BrainNode } from './types';

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

const App: React.FC = () => {
  const [simState, setSimState] = useState<SimulationState>({
    isRunning: false,
    currentFrame: 0,
    metrics: [],
    nodes: INITIAL_NODES,
  });

  const updateSim = useCallback(() => {
    if (!simState.isRunning) return;

    setSimState((prev) => {
      const t = prev.currentFrame;
      const newFrame: MetricFrame = {
        timestamp: t,
        gamma: 0.5 + 0.4 * Math.sin(t * 0.1),
        psi: 0.5 + 0.3 * Math.cos(t * 0.08),
        error: 0.1 + 0.05 * Math.random(),
        phi: Math.sin(t * 0.05) * 10,
        omega: Math.cos(t * 0.05) * 10,
      };

      const updatedNodes = prev.nodes.map(node => ({
        ...node,
        activity: Math.max(0, Math.min(1, Math.random() * (newFrame.gamma + 0.2)))
      }));

      return {
        ...prev,
        currentFrame: t + 1,
        metrics: [...prev.metrics.slice(-100), newFrame],
        nodes: updatedNodes,
      };
    });
  }, [simState.isRunning]);

  useEffect(() => {
    const interval = setInterval(updateSim, 50);
    return () => clearInterval(interval);
  }, [updateSim]);

  const toggleSimulation = () => {
    setSimState(prev => ({ ...prev, isRunning: !prev.isRunning }));
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
