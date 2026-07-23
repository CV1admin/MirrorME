import { BrainNode, MetricFrame } from '../types';

export const DEFAULT_SIMULATION_SEED = 0x4d495252;

function mulberry32(seed: number): () => number {
  let state = seed >>> 0;
  return () => {
    state = (state + 0x6d2b79f5) >>> 0;
    let value = state;
    value = Math.imul(value ^ (value >>> 15), value | 1);
    value ^= value + Math.imul(value ^ (value >>> 7), value | 61);
    return ((value ^ (value >>> 14)) >>> 0) / 4294967296;
  };
}

function frameRandom(seed: number, frame: number): () => number {
  return mulberry32((seed ^ Math.imul(frame + 1, 0x9e3779b1)) >>> 0);
}

export function createBrainNodes(
  seed = DEFAULT_SIMULATION_SEED,
  count = 40,
): BrainNode[] {
  const random = mulberry32(seed);
  return Array.from({ length: count }, (_, index) => ({
    id: `node-${index}`,
    position: [
      (random() - 0.5) * 10,
      (random() - 0.5) * 10,
      (random() - 0.5) * 10,
    ],
    activity: 0,
    type: index % 3 === 0 ? 'cognitive' : index % 3 === 1 ? 'sensory' : 'motor',
  }));
}

export function createMetricFrame(
  frame: number,
  seed = DEFAULT_SIMULATION_SEED,
): MetricFrame {
  if (!Number.isSafeInteger(frame) || frame < 0) {
    throw new RangeError('frame must be a non-negative safe integer');
  }

  const random = frameRandom(seed, frame);
  const faultPhase = frame % 400;
  const injectedFault = faultPhase >= 120 && faultPhase < 130;

  const drift = injectedFault
    ? 0.000012 + random() * 0.000006
    : 0.000004 + random() * 0.000004;
  const error = injectedFault
    ? 0.055 + random() * 0.025
    : drift * 500 + random() * 0.015;

  return {
    timestamp: frame,
    gamma: 40 + 5 * Math.sin(frame * 0.05) + random() * 2,
    psi: injectedFault ? 0.975 + random() * 0.01 : 0.99 + random() * 0.01,
    vireax: injectedFault
      ? 0.975 + random() * 0.01
      : 0.994 + 0.005 * Math.sin(frame * 0.02),
    drift,
    error,
    entropy: 0.4 + 0.1 * Math.cos(frame * 0.03),
  };
}

export function isHealthyFrame(frame: MetricFrame): boolean {
  return frame.vireax >= 0.99 && frame.drift <= 0.00001 && frame.error <= 0.05;
}
