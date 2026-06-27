import React, { useMemo } from 'react';
import { Html } from '@react-three/drei';
import type { ThreeEvent } from '@react-three/fiber';
import * as THREE from 'three';

export interface QuantumNodeMetrics {
  coherence: number;
  spectralDim: number;
  finalState: string;
  count?: number;
}

export interface QuantumNodeData {
  id: string;
  lat: number;
  lng: number;
  score: number;
  label: string;
  color?: string;
  pulse?: boolean;
  metrics: QuantumNodeMetrics;
}

export interface QuantumNodeProps extends QuantumNodeData {
  globeRadius?: number;
  privacyMode?: 'cluster' | 'exact';
  onSelect?: (node: QuantumNodeData) => void;
}

export const quantumResearchNodes: QuantumNodeData[] = [
  {
    id: 'qrc-l3-core-nyc-cluster',
    lat: 40.7128,
    lng: -74.006,
    score: 94,
    label: 'QRC-L3 Core',
    color: '#00ffcc',
    pulse: true,
    metrics: { coherence: 0.85, spectralDim: 2.95, finalState: '(3,3,3)', count: 512 },
  },
  {
    id: 'qrc-l3-mirror-london-cluster',
    lat: 51.5074,
    lng: -0.1278,
    score: 89,
    label: 'QRC-L3 Mirror',
    color: '#00ccff',
    pulse: true,
    metrics: { coherence: 0.82, spectralDim: 2.81, finalState: '(3,3,3)', count: 384 },
  },
  {
    id: 'qrc-l3-edge-tokyo-cluster',
    lat: 35.6762,
    lng: 139.6503,
    score: 87,
    label: 'QRC-L3 Edge',
    color: '#ff00aa',
    pulse: false,
    metrics: { coherence: 0.79, spectralDim: 2.65, finalState: '(6,5,4)', count: 256 },
  },
];

export const latLngToSpherePosition = (
  lat: number,
  lng: number,
  radius: number,
): THREE.Vector3 => {
  const phi = (90 - lat) * (Math.PI / 180);
  const theta = (lng + 180) * (Math.PI / 180);

  return new THREE.Vector3(
    radius * Math.sin(phi) * Math.cos(theta),
    radius * Math.sin(phi) * Math.sin(theta),
    radius * Math.cos(phi),
  );
};

const clamp01 = (value: number): number => Math.max(0, Math.min(1, value));

const QuantumNode: React.FC<QuantumNodeProps> = ({
  id,
  lat,
  lng,
  score,
  label,
  color = '#00ffcc',
  pulse = true,
  metrics,
  globeRadius = 2.1,
  privacyMode = 'cluster',
  onSelect,
}) => {
  const position = useMemo(
    () => latLngToSpherePosition(lat, lng, globeRadius),
    [lat, lng, globeRadius],
  );

  const nodeData = useMemo<QuantumNodeData>(
    () => ({ id, lat, lng, score, label, color, pulse, metrics }),
    [id, lat, lng, score, label, color, pulse, metrics],
  );

  const coherencePct = Math.round(clamp01(metrics.coherence) * 100);

  const handleSelect = (event: ThreeEvent<MouseEvent>) => {
    event.stopPropagation();
    onSelect?.(nodeData);
  };

  return (
    <group position={position} onClick={handleSelect}>
      <mesh onClick={handleSelect}>
        <sphereGeometry args={[0.085, 48, 48]} />
        <meshBasicMaterial color={color} transparent opacity={0.95} />
      </mesh>

      {pulse && (
        <mesh>
          <ringGeometry args={[0.13, 0.19, 64]} />
          <meshBasicMaterial color={color} transparent opacity={0.35} side={THREE.DoubleSide} />
        </mesh>
      )}

      <Html position={[0, 0.25, 0]} style={{ pointerEvents: 'none' }}>
        <div className="min-w-[180px] rounded border border-cyan-400/50 bg-black/80 px-3 py-2 text-xs text-white shadow-xl shadow-cyan-500/10 backdrop-blur-md">
          <div className="flex justify-between gap-3 font-mono text-cyan-300">
            <span>{label}</span>
            <span className="text-emerald-400">CIV1-Q {score}</span>
          </div>

          <div className="mt-2 grid grid-cols-2 gap-x-4 text-[10px] text-slate-300">
            <div>Coherence</div>
            <div className="text-right font-mono">{coherencePct}%</div>

            <div>Spectral Dim</div>
            <div className="text-right font-mono">{metrics.spectralDim.toFixed(2)}</div>

            <div>Final State</div>
            <div className="text-right font-mono">{metrics.finalState}</div>
          </div>

          <div className="mt-2 border-t border-cyan-400/20 pt-1 text-[9px] uppercase tracking-widest text-slate-500">
            {privacyMode === 'cluster' ? 'Cluster coordinate' : 'Exact coordinate'} · click for detail
          </div>
        </div>
      </Html>
    </group>
  );
};

export const QuantumNodeLayer: React.FC<{
  nodes?: QuantumNodeData[];
  globeRadius?: number;
  privacyMode?: 'cluster' | 'exact';
  onSelect?: (node: QuantumNodeData) => void;
}> = ({ nodes = quantumResearchNodes, globeRadius = 2.1, privacyMode = 'cluster', onSelect }) => (
  <>
    {nodes.map((node) => (
      <QuantumNode
        key={node.id}
        {...node}
        globeRadius={globeRadius}
        privacyMode={privacyMode}
        onSelect={onSelect}
      />
    ))}
  </>
);

export default QuantumNode;
