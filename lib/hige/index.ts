export const HIGE_ENGINE_VERSION = "0.1.0";

export type HigeWeights = {
  coherence: number;
  potential: number;
  resonance: number;
};

export const DEFAULT_HIGE_WEIGHTS: HigeWeights = {
  coherence: 0.45,
  potential: 0.25,
  resonance: 0.30,
};
