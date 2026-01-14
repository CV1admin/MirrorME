
import React, { useRef, useMemo } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Float, Sphere, MeshDistortMaterial, Line } from '@react-three/drei';
import * as THREE from 'three';
import { SimulationState, BrainNode } from '../types';

const BrainNodeMesh: React.FC<{ node: BrainNode; gamma: number }> = ({ node, gamma }) => {
  const meshRef = useRef<THREE.Mesh>(null!);
  
  const color = useMemo(() => {
    if (node.type === 'cognitive') return '#22d3ee';
    if (node.type === 'sensory') return '#818cf8';
    return '#fb7185';
  }, [node.type]);

  useFrame((state) => {
    const scale = 0.5 + node.activity * 1.5;
    meshRef.current.scale.lerp(new THREE.Vector3(scale, scale, scale), 0.1);
    
    // Pulse intensity
    if (meshRef.current.material instanceof THREE.MeshStandardMaterial) {
      meshRef.current.material.emissiveIntensity = node.activity * 2;
    }
  });

  return (
    <Sphere ref={meshRef} position={node.position} args={[0.1, 16, 16]}>
      <meshStandardMaterial 
        color={color} 
        emissive={color} 
        emissiveIntensity={1}
        transparent 
        opacity={0.8}
      />
    </Sphere>
  );
};

const Connections: React.FC<{ nodes: BrainNode[]; gamma: number }> = ({ nodes, gamma }) => {
  const points = useMemo(() => {
    const result: [THREE.Vector3, THREE.Vector3][] = [];
    // Just draw some random logical connections for visualization
    for (let i = 0; i < nodes.length; i += 4) {
      if (nodes[i + 1]) {
        result.push([
          new THREE.Vector3(...nodes[i].position),
          new THREE.Vector3(...nodes[i + 1].position)
        ]);
      }
    }
    return result;
  }, [nodes]);

  return (
    <group>
      {points.map((pair, idx) => (
        <Line 
          key={idx}
          points={pair} 
          color="#1e293b" 
          lineWidth={1} 
          transparent 
          opacity={0.2 * gamma} 
        />
      ))}
    </group>
  );
};

const BrainCore: React.FC<{ gamma: number }> = ({ gamma }) => {
  return (
    <Float speed={2} rotationIntensity={0.5} floatIntensity={1}>
      <Sphere args={[2, 32, 32]}>
        <MeshDistortMaterial 
          color="#06b6d4" 
          speed={3} 
          distort={0.4 * gamma} 
          transparent 
          opacity={0.05} 
          wireframe
        />
      </Sphere>
    </Float>
  );
};

const MKoneSimulator: React.FC<{ simState: SimulationState }> = ({ simState }) => {
  const latestMetric = simState.metrics[simState.metrics.length - 1] || { gamma: 0.5 };

  return (
    <div className="w-full h-full bg-[#020617] relative">
      <div className="absolute top-4 left-4 z-10 p-3 bg-slate-900/80 backdrop-blur rounded-lg border border-slate-800/50">
        <h3 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-2">Simulation Space</h3>
        <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-xs">
          <span className="text-slate-400">Vireax State:</span>
          <span className="text-cyan-400 font-bold">STABLE</span>
          <span className="text-slate-400">Node Count:</span>
          <span className="text-slate-200">{simState.nodes.length}</span>
          <span className="text-slate-400">Topology:</span>
          <span className="text-slate-200">MK1_V3</span>
        </div>
      </div>

      <Canvas camera={{ position: [0, 0, 15], fov: 50 }}>
        <ambientLight intensity={0.5} />
        <pointLight position={[10, 10, 10]} intensity={1.5} color="#22d3ee" />
        <pointLight position={[-10, -10, -10]} intensity={0.5} color="#fb7185" />
        
        <BrainCore gamma={latestMetric.gamma} />
        
        {simState.nodes.map(node => (
          <BrainNodeMesh key={node.id} node={node} gamma={latestMetric.gamma} />
        ))}
        
        <Connections nodes={simState.nodes} gamma={latestMetric.gamma} />
        
        <OrbitControls enableDamping dampingFactor={0.05} />
      </Canvas>

      <div className="absolute bottom-4 right-4 z-10 flex gap-2">
        <div className="flex flex-col items-end gap-1">
          <span className="text-[10px] text-slate-500 font-bold uppercase">Axis Lock</span>
          <div className="flex gap-1">
             <button className="w-8 h-8 rounded border border-slate-700 flex items-center justify-center hover:bg-slate-800 transition-colors text-xs text-slate-400">X</button>
             <button className="w-8 h-8 rounded border border-slate-700 flex items-center justify-center hover:bg-slate-800 transition-colors text-xs text-slate-400">Y</button>
             <button className="w-8 h-8 rounded border border-slate-700 flex items-center justify-center hover:bg-slate-800 transition-colors text-xs text-slate-400">Z</button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MKoneSimulator;
