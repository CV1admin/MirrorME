import type { QuantumNodeData } from '../components/sphere/QuantumNodes';

const clamp01 = (value: number): number => Math.max(0, Math.min(1, value));

export const calculateQuantumHealth = (node: QuantumNodeData): number => {
  const spectralComponent = clamp01(node.metrics.spectralDim / 3.0) * 0.45;
  const coherenceComponent = clamp01(node.metrics.coherence) * 0.4;
  const thresholdBonus = node.score > 85 ? 0.15 : 0;

  return clamp01(spectralComponent + coherenceComponent + thresholdBonus);
};

export const calculateQuantumNetworkHealth = (nodes: QuantumNodeData[]): number => {
  if (nodes.length === 0) return 0;

  const total = nodes.reduce((sum, node) => sum + calculateQuantumHealth(node), 0);
  return clamp01(total / nodes.length);
};

export const CIV1_QUANTUM_WEIGHT = 0.12;

export const calculateWeightedQuantumPillar = (nodes: QuantumNodeData[]): number => {
  return calculateQuantumNetworkHealth(nodes) * CIV1_QUANTUM_WEIGHT;
};
