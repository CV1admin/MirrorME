
export enum Role {
  USER = 'user',
  ASSISTANT = 'assistant',
  SYSTEM = 'system'
}

export enum GateStatus {
  GO = 'GO',
  STABILIZING = 'STABILIZING',
  NOGO = 'NO-GO'
}

export interface Message {
  id: string;
  role: Role;
  content: string;
  timestamp: Date;
}

export interface LogicalRepair {
  type: string;
  change: string;
  cost: string;
  notes: string;
}

export interface ContradictionEvent {
  id: string;
  event: string;
  timestamp: number;
  inputs: Record<string, string>;
  formalization: Record<string, string>;
  result: {
    classification: string;
    explanation: string;
  };
  repairs_minimal: LogicalRepair[];
  assumptions: string[];
  constraints_checked: string[];
  violations: string[];
  confidence: number;
  refs: string[];
}

export interface MetricFrame {
  timestamp: number;
  gamma: number;      // Sync proxy (Hz simulated)
  psi: number;        // Snapshot integrity
  vireax: number;     // Control-plane stability
  error: number;      // Reasoning error proxy
  drift: number;      // Temporal jitter (ms)
  entropy: number;    // Hypothesis diversity
}

export interface SimulationState {
  isRunning: boolean;
  gateStatus: GateStatus;
  consecutiveGoFrames: number;
  consecutiveNoGoFrames: number;
  currentFrame: number;
  metrics: MetricFrame[];
  nodes: BrainNode[];
  activeContradiction?: ContradictionEvent;
}

export interface BrainNode {
  id: string;
  position: [number, number, number];
  activity: number;
  type: 'sensory' | 'motor' | 'cognitive';
}

export interface Artifact {
  id: string;
  name: string;
  type: 'json' | 'mp4' | 'csv' | 'logic_repair';
  size: string;
  createdAt: string;
}
