
import React, { useRef, useMemo } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Float, Sphere, MeshDistortMaterial, Line, Points, PointMaterial } from '@react-three/drei';
import * as THREE from 'three';
import { SimulationState, BrainNode } from '../types';

const BrainNodeMesh: React.FC<{ node: BrainNode; vireax: number; gamma: number; drift: number }> = ({ node, vireax, gamma, drift }) => {
  const meshRef = useRef<THREE.Mesh>(null!);
  const initialPos = useMemo(() => new THREE.Vector3(...node.position), [node.position]);
  
  const baseColor = useMemo(() => {
    if (node.type === 'cognitive') return new THREE.Color('#22d3ee');
    if (node.type === 'sensory') return new THREE.Color('#818cf8');
    return new THREE.Color('#fb7185');
  }, [node.type]);

  useFrame((state) => {
    const t = state.clock.getElapsedTime();
    
    // Scale pulse linked to Gamma
    const pulseFactor = Math.sin(t * gamma * 0.5) * 0.2;
    const scale = (0.5 + node.activity * 1.5) + pulseFactor;
    meshRef.current.scale.lerp(new THREE.Vector3(scale, scale, scale), 0.1);
    
    // Position jitter linked to Drift
    if (drift > 0.005) {
      meshRef.current.position.x = initialPos.x + (Math.random() - 0.5) * drift;
      meshRef.current.position.y = initialPos.y + (Math.random() - 0.5) * drift;
      meshRef.current.position.z = initialPos.z + (Math.random() - 0.5) * drift;
    }

    // Color shift based on Stability (vireax)
    if (meshRef.current.material instanceof THREE.MeshStandardMaterial) {
      const stabilityFactor = Math.max(0, 1 - vireax) * 100;
      const finalColor = baseColor.clone().lerp(new THREE.Color('#ff0000'), stabilityFactor);
      meshRef.current.material.color = finalColor;
      meshRef.current.material.emissive = finalColor;
      meshRef.current.material.emissiveIntensity = node.activity * (3 + stabilityFactor * 5);
    }
  });

  return (
    <Sphere ref={meshRef} position={node.position} args={[0.1, 16, 16]}>
      {/* Fix: Use React.createElement to satisfy TypeScript for R3F lowercase intrinsic elements */}
      {React.createElement('meshStandardMaterial', {
        transparent: true,
        opacity: 0.8
      })}
    </Sphere>
  );
};

const BrainCore: React.FC<{ vireax: number }> = ({ vireax }) => {
  return (
    <Float speed={2} rotationIntensity={0.5} floatIntensity={1}>
      <Sphere args={[2.5, 32, 32]}>
        <MeshDistortMaterial 
          color={vireax < 0.99 ? "#ef4444" : "#06b6d4"}
          speed={3} 
          distort={0.4 + (1 - vireax) * 5} 
          transparent 
          opacity={0.08} 
          wireframe
        />
      </Sphere>
    </Float>
  );
};

const MKoneSimulator: React.FC<{ simState: SimulationState }> = ({ simState }) => {
  const latestMetric = simState.metrics[simState.metrics.length - 1] || { gamma: 42, vireax: 0.994, drift: 0.002 };

  return (
    <div className="w-full h-full bg-[#020617] relative">
      <div className="absolute top-4 left-4 z-10 p-3 bg-slate-900/80 backdrop-blur rounded-lg border border-slate-800/50 pointer-events-none">
        <h3 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-2">Cognitive Field Visualizer</h3>
        <div className="grid grid-cols-2 gap-x-6 gap-y-1 text-xs">
          <span className="text-slate-400">Vireax (v):</span>
          <span className={`${latestMetric.vireax < 0.99 ? 'text-red-400' : 'text-cyan-400'} font-bold mono`}>
            {latestMetric.vireax.toFixed(4)}
          </span>
          <span className="text-slate-400">Temporal Drift (Δt):</span>
          <span className="text-slate-200 mono">{latestMetric.drift.toFixed(5)}ms</span>
          <span className="text-slate-400">Coherence (γ):</span>
          <span className="text-indigo-400 font-bold mono">{latestMetric.gamma.toFixed(2)}Hz</span>
        </div>
      </div>

      <Canvas camera={{ position: [0, 0, 15], fov: 45 }}>
        {/* Fix: Use React.createElement for lowercase tags to avoid JSX intrinsic elements TypeScript errors */}
        {React.createElement('fog', { attach: "fog", args: ['#020617', 10, 30] })}
        {React.createElement('ambientLight', { intensity: 0.4 })}
        {React.createElement('pointLight', { position: [10, 10, 10], intensity: 2, color: "#22d3ee" })}
        {React.createElement('pointLight', { position: [-10, -10, -10], intensity: 1, color: "#fb7185" })}
        
        <BrainCore vireax={latestMetric.vireax} />
        
        {simState.nodes.map(node => (
          <BrainNodeMesh 
            key={node.id} 
            node={node} 
            vireax={latestMetric.vireax} 
            gamma={latestMetric.gamma} 
            drift={latestMetric.drift} 
          />
        ))}
        
        <OrbitControls enableDamping dampingFactor={0.05} autoRotate={!simState.isRunning} autoRotateSpeed={0.5} />
      </Canvas>

      <div className="absolute bottom-4 left-4 z-10">
        <div className="flex items-center gap-2 px-3 py-1 bg-slate-900/60 rounded border border-slate-800">
          <div className="w-2 h-2 rounded-full bg-cyan-500 animate-pulse" />
          <span className="text-[9px] font-bold text-slate-400 uppercase tracking-tighter">Live Telemetry Linked</span>
        </div>
      </div>
    </div>
  );
};

export default MKoneSimulator;
