import React, { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';

type WorkspaceTask = {
  id: string;
  title: string;
  area: string;
  done: boolean;
};

type ActivityEntry = {
  id: string;
  message: string;
  timestamp: string;
};

const STORAGE_KEY = 'civilisation-one-dashboard-v1';

const modules = [
  {
    id: 'learning',
    title: 'Learning Hub',
    description: 'Courses, quizzes, simulations, certificates and adaptive pathways.',
    status: 'Planned',
    action: 'Create learning pathway',
  },
  {
    id: 'research',
    title: 'Research Collaboration',
    description: 'Projects, datasets, methods, peer review and replication records.',
    status: 'Development',
    action: 'Start research workspace',
  },
  {
    id: 'knowledge',
    title: 'Knowledge Database',
    description: 'Searchable, versioned and evidence-labelled knowledge resources.',
    status: 'Development',
    action: 'Open resource explorer',
  },
  {
    id: 'laboratory',
    title: 'Virtual Laboratory',
    description: 'Reproducible simulations and Thin Line Lab experiment workflows.',
    status: 'Available',
    action: 'Open Thin Line Lab',
  },
  {
    id: 'community',
    title: 'Community',
    description: 'Study groups, mentoring, expert sessions and structured debate.',
    status: 'Planned',
    action: 'Create community space',
  },
  {
    id: 'sponsorship',
    title: 'Talent Sponsorship',
    description: 'Transparent milestones, funding records and outcome reporting.',
    status: 'Planned',
    action: 'Create sponsorship case',
  },
];

const initialTasks: WorkspaceTask[] = [
  { id: 'task-1', title: 'Define first public learning pathway', area: 'Learning', done: false },
  { id: 'task-2', title: 'Connect OIIIDS resource publication API', area: 'Infrastructure', done: false },
  { id: 'task-3', title: 'Prepare research submission workflow', area: 'Research', done: false },
  { id: 'task-4', title: 'Review governance and safeguarding gates', area: 'Governance', done: true },
];

const statusClass = (status: string) => {
  if (status === 'Available') return 'border-emerald-500/30 bg-emerald-500/10 text-emerald-300';
  if (status === 'Development') return 'border-amber-500/30 bg-amber-500/10 text-amber-300';
  return 'border-slate-700 bg-slate-800 text-slate-400';
};

const CivilisationDashboard: React.FC = () => {
  const [query, setQuery] = useState('');
  const [activeArea, setActiveArea] = useState('All');
  const [tasks, setTasks] = useState<WorkspaceTask[]>(initialTasks);
  const [draftTask, setDraftTask] = useState('');
  const [activity, setActivity] = useState<ActivityEntry[]>([]);
  const [notice, setNotice] = useState('');

  useEffect(() => {
    const stored = window.localStorage.getItem(STORAGE_KEY);
    if (!stored) return;

    try {
      const parsed = JSON.parse(stored) as { tasks?: WorkspaceTask[]; activity?: ActivityEntry[] };
      if (Array.isArray(parsed.tasks)) setTasks(parsed.tasks);
      if (Array.isArray(parsed.activity)) setActivity(parsed.activity);
    } catch {
      window.localStorage.removeItem(STORAGE_KEY);
    }
  }, []);

  useEffect(() => {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify({ tasks, activity }));
  }, [tasks, activity]);

  const filteredModules = useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase();
    return modules.filter((module) => {
      const matchesQuery = !normalizedQuery || `${module.title} ${module.description}`.toLowerCase().includes(normalizedQuery);
      const matchesArea = activeArea === 'All' || module.status === activeArea;
      return matchesQuery && matchesArea;
    });
  }, [query, activeArea]);

  const completion = tasks.length === 0 ? 0 : Math.round((tasks.filter((task) => task.done).length / tasks.length) * 100);

  const recordActivity = (message: string) => {
    setActivity((previous) => [
      { id: `${Date.now()}-${Math.random()}`, message, timestamp: new Date().toLocaleString() },
      ...previous,
    ].slice(0, 8));
  };

  const handleModuleAction = (title: string, status: string) => {
    if (status === 'Available') {
      setNotice(`${title} is available through the linked workspace.`);
      recordActivity(`Opened ${title}`);
      return;
    }

    const message = `${title} requires backend integration before it can become operational.`;
    setNotice(message);
    recordActivity(`Requested ${title} functionality`);
  };

  const toggleTask = (taskId: string) => {
    setTasks((previous) => previous.map((task) => task.id === taskId ? { ...task, done: !task.done } : task));
    const task = tasks.find((item) => item.id === taskId);
    if (task) recordActivity(`${task.done ? 'Reopened' : 'Completed'} task: ${task.title}`);
  };

  const addTask = (event: React.FormEvent) => {
    event.preventDefault();
    const title = draftTask.trim();
    if (!title) return;

    setTasks((previous) => [
      ...previous,
      { id: `task-${Date.now()}`, title, area: 'General', done: false },
    ]);
    setDraftTask('');
    recordActivity(`Created task: ${title}`);
  };

  const resetWorkspace = () => {
    setTasks(initialTasks);
    setActivity([]);
    setNotice('Local dashboard workspace reset.');
    window.localStorage.removeItem(STORAGE_KEY);
  };

  return (
    <div className="p-4 md:p-8 max-w-7xl mx-auto space-y-6 overflow-y-auto h-full">
      <header className="flex flex-col xl:flex-row xl:items-end xl:justify-between gap-5">
        <div>
          <div className="text-[10px] uppercase tracking-[0.3em] text-cyan-500 font-bold mb-2">Civilisation.One Control Surface</div>
          <h2 className="text-3xl font-bold text-slate-100 mb-2">Platform Dashboard</h2>
          <p className="text-slate-400 max-w-3xl">
            Interactive local workspace for navigating platform modules, tracking implementation tasks and exposing production blockers.
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Link to="/system-map" className="px-4 py-2 rounded-lg border border-cyan-500/30 bg-cyan-500/10 text-cyan-300 text-sm font-bold hover:bg-cyan-500/20">
            Full System Map
          </Link>
          <Link to="/oiiids-operations" className="px-4 py-2 rounded-lg border border-indigo-500/30 bg-indigo-500/10 text-indigo-300 text-sm font-bold hover:bg-indigo-500/20">
            OIIIDS Operations
          </Link>
        </div>
      </header>

      {notice && (
        <div className="flex items-start justify-between gap-4 rounded-xl border border-cyan-500/30 bg-cyan-500/10 px-4 py-3 text-sm text-cyan-200">
          <span>{notice}</span>
          <button type="button" onClick={() => setNotice('')} className="text-cyan-400 hover:text-white">Dismiss</button>
        </div>
      )}

      <section className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        {[
          ['Platform mode', 'Local MVP'],
          ['Production gate', 'Closed'],
          ['Task completion', `${completion}%`],
          ['Operational modules', `${modules.filter((module) => module.status === 'Available').length}/${modules.length}`],
        ].map(([label, value]) => (
          <div key={label} className="rounded-xl border border-slate-800 bg-slate-900 p-4">
            <div className="text-[10px] uppercase tracking-widest text-slate-500 font-bold mb-2">{label}</div>
            <div className="text-xl font-black text-slate-100">{value}</div>
          </div>
        ))}
      </section>

      <section className="rounded-2xl border border-slate-800 bg-slate-900 p-5 space-y-4">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-3">
          <div>
            <h3 className="text-sm font-bold text-slate-100">Platform Modules</h3>
            <p className="text-xs text-slate-500 mt-1">Search and inspect the current implementation state.</p>
          </div>
          <div className="flex flex-col sm:flex-row gap-2">
            <input
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="Search modules"
              className="min-w-[220px] rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-200 outline-none focus:border-cyan-500"
            />
            <select
              value={activeArea}
              onChange={(event) => setActiveArea(event.target.value)}
              className="rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-200 outline-none focus:border-cyan-500"
            >
              <option>All</option>
              <option>Available</option>
              <option>Development</option>
              <option>Planned</option>
            </select>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {filteredModules.map((module) => (
            <article key={module.id} className="rounded-xl border border-slate-800 bg-slate-950 p-4 flex flex-col gap-4">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <h4 className="font-bold text-slate-100">{module.title}</h4>
                  <p className="text-sm text-slate-400 mt-2">{module.description}</p>
                </div>
                <span className={`shrink-0 rounded-full border px-2 py-1 text-[10px] uppercase font-bold ${statusClass(module.status)}`}>
                  {module.status}
                </span>
              </div>
              {module.id === 'laboratory' ? (
                <Link to="/thin-line-theory" onClick={() => recordActivity('Opened Thin Line Lab')} className="mt-auto text-center rounded-lg border border-cyan-500/30 bg-cyan-500/10 px-3 py-2 text-xs font-bold text-cyan-300 hover:bg-cyan-500/20">
                  {module.action}
                </Link>
              ) : module.id === 'knowledge' ? (
                <Link to="/oiiids-operations" onClick={() => recordActivity('Opened OIIIDS Resource Explorer')} className="mt-auto text-center rounded-lg border border-indigo-500/30 bg-indigo-500/10 px-3 py-2 text-xs font-bold text-indigo-300 hover:bg-indigo-500/20">
                  {module.action}
                </Link>
              ) : (
                <button type="button" onClick={() => handleModuleAction(module.title, module.status)} className="mt-auto rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-xs font-bold text-slate-300 hover:border-cyan-500/40 hover:text-cyan-300">
                  {module.action}
                </button>
              )}
            </article>
          ))}
        </div>

        {filteredModules.length === 0 && (
          <div className="rounded-xl border border-dashed border-slate-700 p-8 text-center text-sm text-slate-500">No modules match the current filters.</div>
        )}
      </section>

      <section className="grid grid-cols-1 xl:grid-cols-3 gap-5">
        <div className="xl:col-span-2 rounded-2xl border border-slate-800 bg-slate-900 p-5">
          <div className="flex items-center justify-between gap-3 mb-4">
            <div>
              <h3 className="text-sm font-bold text-slate-100">Implementation Tasks</h3>
              <p className="text-xs text-slate-500 mt-1">Saved in this browser until a durable backend is connected.</p>
            </div>
            <button type="button" onClick={resetWorkspace} className="text-xs text-slate-500 hover:text-red-300">Reset</button>
          </div>

          <form onSubmit={addTask} className="flex gap-2 mb-4">
            <input
              value={draftTask}
              onChange={(event) => setDraftTask(event.target.value)}
              placeholder="Add implementation task"
              className="flex-1 rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-200 outline-none focus:border-cyan-500"
            />
            <button type="submit" className="rounded-lg bg-cyan-500 px-4 py-2 text-sm font-black text-slate-950 hover:bg-cyan-400">Add</button>
          </form>

          <div className="space-y-2">
            {tasks.map((task) => (
              <label key={task.id} className="flex items-center gap-3 rounded-lg border border-slate-800 bg-slate-950 px-3 py-3 cursor-pointer">
                <input type="checkbox" checked={task.done} onChange={() => toggleTask(task.id)} className="accent-cyan-500" />
                <span className={`flex-1 text-sm ${task.done ? 'line-through text-slate-600' : 'text-slate-300'}`}>{task.title}</span>
                <span className="text-[10px] uppercase tracking-wider text-slate-600">{task.area}</span>
              </label>
            ))}
          </div>
        </div>

        <aside className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
          <h3 className="text-sm font-bold text-slate-100 mb-1">Recent Activity</h3>
          <p className="text-xs text-slate-500 mb-4">Local dashboard events only; not Observer audit records.</p>
          <div className="space-y-3">
            {activity.length === 0 && <div className="text-sm text-slate-600">No activity recorded.</div>}
            {activity.map((entry) => (
              <div key={entry.id} className="border-l-2 border-cyan-500/40 pl-3">
                <div className="text-sm text-slate-300">{entry.message}</div>
                <div className="text-[10px] text-slate-600 mt-1">{entry.timestamp}</div>
              </div>
            ))}
          </div>
        </aside>
      </section>

      <section className="rounded-2xl border border-red-500/20 bg-red-500/5 p-5">
        <div className="text-[10px] uppercase tracking-widest text-red-400 font-bold mb-2">Production Blockers</div>
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-3 text-sm text-slate-300">
          <div className="rounded-lg border border-red-500/10 bg-slate-950 p-3">Authenticated Civilisation.One API</div>
          <div className="rounded-lg border border-red-500/10 bg-slate-950 p-3">Durable user and project persistence</div>
          <div className="rounded-lg border border-red-500/10 bg-slate-950 p-3">Authorization and governance enforcement</div>
          <div className="rounded-lg border border-red-500/10 bg-slate-950 p-3">Live OIIIDS and Observer integration</div>
        </div>
      </section>
    </div>
  );
};

export default CivilisationDashboard;
