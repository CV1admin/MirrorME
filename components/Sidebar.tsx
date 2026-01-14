
import React from 'react';
import { NavLink } from 'react-router-dom';

const Sidebar: React.FC = () => {
  const links = [
    { to: '/workspace', label: 'Dashboard', icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" /></svg>
    )},
    { to: '/artifacts', label: 'Artifacts', icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" /></svg>
    )},
    { to: '/settings', label: 'Engine Config', icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
    )},
  ];

  return (
    <nav className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col p-4 gap-2">
      <div className="px-4 py-4 mb-4">
        <div className="flex items-center gap-2 mb-1">
          <div className="w-6 h-6 bg-cyan-500 rounded-sm" />
          <span className="font-bold text-xl">MirrorMe</span>
        </div>
        <p className="text-[10px] uppercase tracking-tighter text-slate-500 font-bold">Science & Engineering Platform</p>
      </div>

      {links.map((link) => (
        <NavLink
          key={link.to}
          to={link.to}
          className={({ isActive }) => 
            `flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
              isActive 
              ? 'bg-slate-800 text-cyan-400 border border-slate-700' 
              : 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-200'
            }`
          }
        >
          {link.icon}
          <span className="font-medium text-sm">{link.label}</span>
        </NavLink>
      ))}

      <div className="mt-auto pt-4 border-t border-slate-800">
        <div className="p-4 bg-slate-800/30 rounded-xl border border-slate-800/50">
          <h4 className="text-[10px] uppercase text-slate-500 font-bold mb-2">Workspace Health</h4>
          <div className="space-y-2">
            <div className="flex justify-between items-center text-xs">
              <span className="text-slate-400">Node Sync</span>
              <span className="text-green-400">98.2%</span>
            </div>
            <div className="w-full h-1 bg-slate-700 rounded-full overflow-hidden">
              <div className="w-[98%] h-full bg-cyan-500" />
            </div>
            <div className="flex justify-between items-center text-xs">
              <span className="text-slate-400">Entropy</span>
              <span className="text-orange-400">Low</span>
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Sidebar;
