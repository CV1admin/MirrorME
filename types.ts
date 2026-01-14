
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

export type MessageStatus = 'pending' | 'streaming' | 'sent' | 'failed' | 'ack';

export interface AuditMetadata {
  module_id: string;
  assumptions: string[];
  constraints_checked: string[];
  violations: string[];
  confidence: number;
  refs: string[];
  telemetry_snapshot?: {
    gamma_hz: number;
    vireax_v: number;
    drift_seconds: number;
    error_epsilon: number;
  };
}

export interface Message {
  id: string;
  client_msg_id?: string;
  role: Role;
  content: string;
  timestamp: Date;
  status: MessageStatus;
  audit?: AuditMetadata;
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
  gamma: number;      // Sync proxy (Hz)
  psi: number;        // Integrity (0..1)
  vireax: number;     // Stability (0..1)
  error: number;      // Reasoning Error (0..1)
  drift: number;      // Temporal jitter (seconds, canonical)
  entropy: number;    // Diversity (0..1)
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
