export const HIGE_ENGINE_VERSION = "0.1.0";

export type HigeWeights = {
  coherence: number;
  potential: number;
  resonance: number;
};

export type HigeMetrics = {
  purity: number;
  coherenceNorm: number;
  entropy: number;
  potentialNorm: number;
  resonance: number;
  resonanceNorm: number;
  harmony: number;
  informationRatio: number;
};

export const DEFAULT_HIGE_WEIGHTS: HigeWeights = {
  coherence: 0.45,
  potential: 0.25,
  resonance: 0.30,
};

const clamp01 = (value: number): number => Math.max(0, Math.min(1, value));

const normalizeWeights = (weights: HigeWeights): HigeWeights => {
  const total = weights.coherence + weights.potential + weights.resonance;
  if (!Number.isFinite(total) || total <= 0) return DEFAULT_HIGE_WEIGHTS;
  return {
    coherence: weights.coherence / total,
    potential: weights.potential / total,
    resonance: weights.resonance / total,
  };
};

export const computeHarmony = (
  coherenceNorm: number,
  potentialNorm: number,
  resonanceNorm: number,
  weights: HigeWeights = DEFAULT_HIGE_WEIGHTS,
): number => {
  const w = normalizeWeights(weights);
  return clamp01(
    w.coherence * clamp01(coherenceNorm) +
      w.potential * clamp01(potentialNorm) +
      w.resonance * clamp01(resonanceNorm),
  );
};

export const computePurity = (rho: number[][]): number => {
  let value = 0;
  for (let i = 0; i < rho.length; i += 1) {
    for (let j = 0; j < rho.length; j += 1) {
      value += (rho[i]?.[j] ?? 0) * (rho[j]?.[i] ?? 0);
    }
  }
  return value;
};

export const normalizeCoherence = (purity: number, dimension: number): number => {
  if (dimension <= 1) return clamp01(purity);
  const minimum = 1 / dimension;
  return clamp01((purity - minimum) / (1 - minimum));
};

export const computeDiagonalEntropy = (rho: number[][]): number => {
  let entropy = 0;
  for (let i = 0; i < rho.length; i += 1) {
    const p = Math.max(0, rho[i]?.[i] ?? 0);
    if (p > 0) entropy -= p * Math.log(p);
  }
  return entropy;
};

export const normalizePotential = (entropy: number, dimension: number): number => {
  if (dimension <= 1) return 0;
  return clamp01(entropy / Math.log(dimension));
};

export const computeResonance = (
  previousRho: number[][],
  currentRho: number[][],
  dt = 1,
): number => {
  const safeDt = Math.max(dt, Number.EPSILON);
  let sum = 0;
  for (let i = 0; i < currentRho.length; i += 1) {
    for (let j = 0; j < currentRho.length; j += 1) {
      const delta = ((currentRho[i]?.[j] ?? 0) - (previousRho[i]?.[j] ?? 0)) / safeDt;
      sum += delta * delta;
    }
  }
  return Math.sqrt(sum);
};

export const normalizeResonance = (resonance: number, kappa = 1): number => {
  const safeKappa = Math.max(kappa, Number.EPSILON);
  return clamp01(resonance / (resonance + safeKappa));
};

export const computeInformationRatio = (
  coherenceNorm: number,
  potentialNorm: number,
  epsilon = 1e-9,
): number => coherenceNorm / (potentialNorm + epsilon);

export const computeHigeMetrics = (
  previousRho: number[][],
  currentRho: number[][],
  options?: {
    dt?: number;
    kappa?: number;
    epsilon?: number;
    weights?: HigeWeights;
  },
): HigeMetrics => {
  const dimension = currentRho.length;
  const purity = computePurity(currentRho);
  const coherenceNorm = normalizeCoherence(purity, dimension);
  const entropy = computeDiagonalEntropy(currentRho);
  const potentialNorm = normalizePotential(entropy, dimension);
  const resonance = computeResonance(previousRho, currentRho, options?.dt ?? 1);
  const resonanceNorm = normalizeResonance(resonance, options?.kappa ?? 1);
  const harmony = computeHarmony(coherenceNorm, potentialNorm, resonanceNorm, options?.weights);
  const informationRatio = computeInformationRatio(coherenceNorm, potentialNorm, options?.epsilon ?? 1e-9);

  return {
    purity,
    coherenceNorm,
    entropy,
    potentialNorm,
    resonance,
    resonanceNorm,
    harmony,
    informationRatio,
  };
};
