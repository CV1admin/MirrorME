import React from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Stars } from '@react-three/drei';
import { QuantumNodeLayer, quantumResearchNodes } from './QuantumNodes';
import { calculateQuantumNetworkHealth } from '../../lib/civScore';

const QuantumHubSphere: React.FC = () => {
  const networkHealth = calculateQuantumNetworkHealth(quantumResearchNodes);

  return (
    <section className="rounded-2xl border border-cyan-500/25 bg-slate-950 p-4">
      <div className="mb-3 flex items-end justify-between gap-4">
        <div>
          <h3 className="text-xs font-bold uppercase tracking-widest text-cyan-300">Civilisation.One Hub Sphere</h3>
          <p className="mt-1 text-xs text-slate-500">
            Quantum research clusters. Coordinates are public cluster anchors, not exact personal locations.
          </p>
        </div>
        <div className="rounded-xl border border-emerald-500/25 bg-emerald-500/10 px-3 py-2 text-right">
          <div className="text-[10px] uppercase tracking-widest text-emerald-300">Quantum Health</div>
          <div className="font-mono text-lg font-black text-emerald-200">{Math.round(networkHealth * 100)}%</div>
        </div>
      </div>

      <div className="h-[420px] overflow-hidden rounded-xl border border-slate-800 bg-black">
        <Canvas camera={{ position: [0, 0, 6], fov: 45 }}>
          <ambientLight intensity={0.35} />
          <pointLight position={[4, 4, 4]} intensity={1.2} />
          <Stars radius={80} depth={40} count={1200} factor={3} saturation={0} fade speed={0.3} />

          <mesh>
            <sphereGeometry args={[2, 64, 64]} />
            <meshStandardMaterial color="#07111f" roughness={0.95} metalness={0.15} wireframe />
          </mesh>

          <QuantumNodeLayer nodes={quantumResearchNodes} globeRadius={2.1} privacyMode="cluster" />
          <OrbitControls enablePan={false} minDistance={3.2} maxDistance={8} />
        </Canvas>
      </div>
    </section>
  );
};

export default QuantumHubSphere;
