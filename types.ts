
export enum Role {
  USER = 'user',
  ASSISTANT = 'assistant',
  SYSTEM = 'system'
}

export interface Message {
  id: string;
  role: Role;
  content: string;
  timestamp: Date;
}

export interface MetricFrame {
  timestamp: number;
  gamma: number;
  psi: number;
  error: number;
  phi: number;
  omega: number;
}

export interface SimulationState {
  isRunning: boolean;
  currentFrame: number;
  metrics: MetricFrame[];
  nodes: BrainNode[];
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
  type: 'json' | 'mp4' | 'csv';
  size: string;
  createdAt: string;
}
