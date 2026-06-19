import React from 'react';

const CivilisationDashboard: React.FC = () => {
  const missionPillars = [
    'Open scientific education',
    'AI-assisted learning',
    'Collaborative research',
    'Ethical innovation',
    'Talent sponsorship',
    'Scientific simulations',
    'Collective knowledge verification',
    'Space exploration and future-oriented research',
  ];

  const coreQuestions = [
    'What is the nature and meaning of life?',
    'How did the universe originate?',
    'How do consciousness and perception emerge?',
    'How does quantum physics change our understanding of reality?',
    'How does AI influence human knowledge, belief, creativity, and decision-making?',
    'How can scientific progress improve happiness, safety, education, and human cooperation?',
  ];

  const structureBlocks = [
    {
      title: 'Learning Hub',
      items: [
        'Interactive courses, quizzes, practical exercises, simulations, and certificates',
        'Disciplines: math, physics, astronomy, biology, chemistry, computer science, AI, quantum, engineering, climate, philosophy of science, ethics',
        'Classification: established knowledge, active research, competing interpretation, speculative hypothesis, independently submitted theory',
      ],
    },
    {
      title: 'Research Collaboration Space',
      items: [
        'Project creation, team formation, datasets/code sharing, simulation runs, research logs',
        'Preprints, reports, peer review, revision tracking, replication support, mentorship',
        'Methodology, assumptions, funding, conflicts, evidence level, and verification status visibility',
      ],
    },
    {
      title: 'Talent Sponsorship',
      items: [
        'Support students, independent researchers, educators, teams, open-source, and underfunded disciplines',
        'Transparent milestones, expenditure logs, and outcome reporting',
      ],
    },
    {
      title: 'Interactive Community',
      items: [
        'Q&A, debates, study groups, research communities, expert sessions, peer mentoring',
        'Reputation based on citations, verification success, and ethical conduct',
      ],
    },
  ];

  const featureTools = [
    'Searchable Knowledge Database',
    'AI-Assisted Tutoring',
    'Virtual Laboratory',
    'Scholarship and Grant Finder',
  ];

  const profileDimensions = [
    'Knowledge',
    'Verification',
    'Learning',
    'Collaboration',
    'Creativity',
    'Ethics',
    'Wellbeing',
    'Contribution',
  ];

  const governanceBodies = [
    'Scientific review',
    'AI ethics',
    'Data protection',
    'Financial oversight',
    'Child safety',
    'Research integrity',
    'Appeals and dispute resolution',
    'Community moderation',
  ];

  const legalFramework = [
    'Data protection and privacy',
    'Copyright and educational licensing',
    'Child and student safeguarding',
    'Consumer rights and accessibility',
    'Research ethics and AI transparency',
    'Financial transactions and sponsorship disclosure',
    'International data transfers and certification claims',
  ];

  const decentralisedStatements = [
    {
      title: '1. Purpose',
      text: 'Civilisation.One advances universal education, scientific verification, and ethical AI through open, decentralised collaboration.',
    },
    {
      title: '2. Decentralisation by Design',
      text: 'No single node controls knowledge or direction. Governance emerges through transparent standards and mutual verification.',
    },
    {
      title: '3. Open Knowledge and Verifiability',
      text: 'Models, simulations, and learning pathways are designed to be inspectable, testable, and reproducible.',
    },
    {
      title: '4. Education Without Barriers',
      text: 'Age-universal access with complexity scaling, supporting early learners, students, and experts from the same core structure.',
    },
    {
      title: '5. Science as a Living Process',
      text: 'Hypotheses are encouraged, challenged, refined, or discarded through evidence, coherence, and peer review.',
    },
    {
      title: '6. Human-AI Co-Learning',
      text: 'AI assists with simulation, explanation, and reasoning under auditable constraints and clear accountability.',
    },
    {
      title: '7. Ethical Alignment',
      text: 'Protocols enforce no-harm, transparency, fairness, and respect for human agency. Ethics is built-in, not bolted-on.',
    },
    {
      title: '8. Cultural and Political Neutrality',
      text: 'Not bound to any nation or ideology. Diverse perspectives are welcome while remaining evidence-grounded.',
    },
    {
      title: '9. Collective Intelligence',
      text: 'Constructive dissent and contradiction are treated as engines of understanding, not threats to it.',
    },
    {
      title: '10. Stewardship of the Future',
      text: 'Curricula, tools, and AI systems are designed for long-term civilisational stability, sustainability, and wisdom.',
    },
    {
      title: '11. Transparency of Power',
      text: 'Decision systems, algorithms, and governance mechanisms are visible and accountable. Influence is earned by contribution.',
    },
    {
      title: '12. Invitation',
      text: 'Open to learners, educators, scientists, builders, and explorers. Participation is shared stewardship of knowledge.',
    },
  ];

  const operatingPrinciples = [
    {
      title: 'Verification over authority',
      text: 'Claims gain status through reproducibility, traceable reasoning, and evidence, not titles, brands, or hierarchy.',
    },
    {
      title: 'Transparency by default',
      text: 'When AI assists, assumptions, limitations, and decision criteria are published whenever feasible.',
    },
    {
      title: 'No-harm and human agency',
      text: 'People are protected from manipulation and coercion, with the right to opt out, disagree, and fork.',
    },
  ];

  const participationTracks = [
    {
      title: 'Learners',
      text: 'Follow guided pathways, explore simulations, and test understanding through interactive problem-solving.',
    },
    {
      title: 'Educators',
      text: 'Publish lessons, verification exercises, and curricula that others can reproduce and improve.',
    },
    {
      title: 'Researchers and Builders',
      text: 'Contribute models, datasets, experiments, code, and peer review to help the network converge on what holds up.',
    },
  ];

  const architectureLayers = [
    {
      title: 'Browser / PWA',
      stack: 'Next.js + TypeScript',
      detail: 'Local encrypted profile and consent state',
    },
    {
      title: 'Civilisation.One API',
      stack: 'FastAPI + Python',
      detail: 'Authentication, governance, moderation',
    },
    {
      title: 'PostgreSQL',
      stack: 'PostGIS + RLS',
      detail: 'Platform records',
    },
    {
      title: 'Worker',
      stack: 'Background processing',
      detail: 'Notifications, metrics and reports',
    },
    {
      title: 'S3-compatible object storage',
      stack: 'Blob and evidence layer',
      detail: 'Evidence, images, reports and datasets',
    },
  ];

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="flex items-end justify-between gap-4">
        <div>
          <h2 className="text-3xl font-bold text-slate-100 mb-2">Civilisation One</h2>
          <p className="text-slate-400">Global scientific learning, research, and human development platform.</p>
        </div>
        <div className="px-5 py-3 rounded-xl border border-cyan-500/30 bg-cyan-500/10 text-cyan-300">
          <div className="text-[10px] uppercase tracking-widest font-bold">Positioning</div>
          <div className="text-sm font-black leading-tight">Open Scientific Learning and Collaboration Ecosystem</div>
        </div>
      </div>

      <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
        <h3 className="text-xs uppercase tracking-widest text-cyan-400 font-bold mb-4">Vision and Mission</h3>
        <p className="text-sm text-slate-300 mb-4">
          To create a globally accessible platform for scientific learning, research, innovation, and interdisciplinary collaboration,
          helping people understand the universe, develop their abilities, and contribute responsibly to civilisation.
        </p>
        <div className="flex flex-wrap gap-2">
          {missionPillars.map((pillar) => (
            <span key={pillar} className="px-2.5 py-1 rounded-full text-[11px] border border-cyan-500/20 bg-cyan-500/10 text-cyan-300">
              {pillar}
            </span>
          ))}
        </div>
      </section>

      <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
        <h3 className="text-xs uppercase tracking-widest text-cyan-400 font-bold mb-4">Core Research Motivation</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {coreQuestions.map((question) => (
            <div key={question} className="p-3 rounded-xl border border-slate-800 bg-slate-950 text-sm text-slate-300">
              {question}
            </div>
          ))}
        </div>
        <p className="text-xs text-slate-500 mt-4">
          Participation in social research must be voluntary, consent-based, privacy-protected, and revocable.
        </p>
      </section>

      <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
        <h3 className="text-xs uppercase tracking-widest text-cyan-400 font-bold mb-4">Platform Structure</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {structureBlocks.map((block) => (
            <div key={block.title} className="p-4 rounded-xl border border-slate-800 bg-slate-950">
              <h4 className="text-sm font-bold text-slate-200 mb-2">{block.title}</h4>
              <ul className="space-y-2 text-sm text-slate-400">
                {block.items.map((item) => (
                  <li key={item} className="border border-slate-800 rounded-md px-2 py-1.5">{item}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </section>

      <section className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
          <h3 className="text-xs uppercase tracking-widest text-cyan-400 font-bold mb-4">Features and Tools</h3>
          <ul className="space-y-2 text-sm text-slate-300">
            {featureTools.map((tool) => (
              <li key={tool} className="p-2 rounded-md border border-slate-800 bg-slate-950">{tool}</li>
            ))}
          </ul>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
          <h3 className="text-xs uppercase tracking-widest text-cyan-400 font-bold mb-4">Civilisation 2 Profile Dimensions</h3>
          <div className="flex flex-wrap gap-2">
            {profileDimensions.map((dimension) => (
              <span key={dimension} className="px-3 py-1 text-xs rounded-full border border-emerald-500/25 bg-emerald-500/10 text-emerald-300">
                {dimension}
              </span>
            ))}
          </div>
          <p className="text-xs text-slate-500 mt-4">
            Placeholder formula: C2 = wK*K + wV*V + wL*L + wC*C + wR*R + wE*E + wW*W + wI*I
          </p>
        </div>
      </section>

      <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
        <h3 className="text-xs uppercase tracking-widest text-cyan-400 font-bold mb-4">Happiness and Safety Data Principles</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm text-slate-300">
          <div className="p-3 rounded-xl border border-slate-800 bg-slate-950">Use aggregate statistics wherever possible.</div>
          <div className="p-3 rounded-xl border border-slate-800 bg-slate-950">Collect sensitive data only with explicit consent and clear purpose.</div>
          <div className="p-3 rounded-xl border border-slate-800 bg-slate-950">Publish retention, access, opt-out, and correction policies.</div>
          <div className="p-3 rounded-xl border border-slate-800 bg-slate-950">Protect autonomy, privacy, and intellectual freedom.</div>
        </div>
      </section>

      <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
        <h3 className="text-xs uppercase tracking-widest text-cyan-400 font-bold mb-4">Infrastructure</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 rounded-xl border border-slate-800 bg-slate-950">
            <h4 className="text-sm font-bold text-slate-200 mb-1">DePIN Nodes</h4>
            <p className="text-sm text-slate-400">Distributed physical infrastructure nodes for resilient computation and sensing.</p>
          </div>
          <div className="p-4 rounded-xl border border-slate-800 bg-slate-950">
            <h4 className="text-sm font-bold text-slate-200 mb-1">QVIREAX Quantum Network Research</h4>
            <p className="text-sm text-slate-400">Experimental pathway for high-fidelity synchronization and secure distributed reasoning.</p>
          </div>
          <div className="p-4 rounded-xl border border-slate-800 bg-slate-950">
            <h4 className="text-sm font-bold text-slate-200 mb-1">Governance/Audit Layer</h4>
            <p className="text-sm text-slate-400">Policy, traceability, and accountability controls for system decisions.</p>
          </div>
          <div className="p-4 rounded-xl border border-slate-800 bg-slate-950">
            <h4 className="text-sm font-bold text-slate-200 mb-1">Token/Reward Systems</h4>
            <p className="text-sm text-slate-400">Incentive mechanics for contribution quality, transparency, and long-term alignment.</p>
          </div>
        </div>
      </section>

      <section className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
          <h3 className="text-xs uppercase tracking-widest text-cyan-400 font-bold mb-4">Governance and Scientific Integrity</h3>
          <ul className="space-y-2 text-sm text-slate-300">
            {governanceBodies.map((body) => (
              <li key={body} className="p-2 rounded-md border border-slate-800 bg-slate-950">{body}</li>
            ))}
          </ul>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
          <h3 className="text-xs uppercase tracking-widest text-cyan-400 font-bold mb-4">Legal and Compliance Framework</h3>
          <ul className="space-y-2 text-sm text-slate-300">
            {legalFramework.map((entry) => (
              <li key={entry} className="p-2 rounded-md border border-slate-800 bg-slate-950">{entry}</li>
            ))}
          </ul>
        </div>
      </section>

      <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
        <h3 className="text-xs uppercase tracking-widest text-cyan-400 font-bold mb-4">Decentralised Global Organisation Statements</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {decentralisedStatements.map((statement) => (
            <div key={statement.title} className="p-3 rounded-xl border border-slate-800 bg-slate-950">
              <h4 className="text-xs font-bold uppercase tracking-wide text-cyan-300 mb-1">{statement.title}</h4>
              <p className="text-sm text-slate-300">{statement.text}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
          <h3 className="text-xs uppercase tracking-widest text-cyan-400 font-bold mb-4">Principles</h3>
          <div className="space-y-3">
            {operatingPrinciples.map((principle) => (
              <div key={principle.title} className="p-3 rounded-xl border border-slate-800 bg-slate-950">
                <h4 className="text-sm font-bold text-slate-200 mb-1">{principle.title}</h4>
                <p className="text-sm text-slate-400">{principle.text}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
          <h3 className="text-xs uppercase tracking-widest text-cyan-400 font-bold mb-4">Participate</h3>
          <div className="space-y-3">
            {participationTracks.map((track) => (
              <div key={track.title} className="p-3 rounded-xl border border-slate-800 bg-slate-950">
                <h4 className="text-sm font-bold text-slate-200 mb-1">{track.title}</h4>
                <p className="text-sm text-slate-400">{track.text}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
        <h3 className="text-xs uppercase tracking-widest text-cyan-400 font-bold mb-4">Reference Architecture</h3>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {architectureLayers.map((layer) => (
            <div key={layer.title} className="p-3 rounded-xl border border-slate-800 bg-slate-950">
              <h4 className="text-sm font-bold text-slate-100">{layer.title}</h4>
              <p className="text-xs text-cyan-300 mt-1">{layer.stack}</p>
              <p className="text-sm text-slate-400 mt-1">{layer.detail}</p>
            </div>
          ))}
        </div>
        <div className="mt-4 p-3 rounded-xl border border-slate-800 bg-slate-950">
          <p className="text-xs text-slate-400">
            Data flow: Browser/PWA -&gt; HTTPS JSON -&gt; Civilisation.One API -&gt; PostgreSQL and Worker pipelines, with evidence and large artifacts stored in S3-compatible object storage.
          </p>
        </div>
      </section>

      <section className="rounded-2xl border border-cyan-500/25 bg-cyan-500/10 p-6">
        <h3 className="text-xs uppercase tracking-widest text-cyan-300 font-bold mb-3">Proposed Positioning Statement</h3>
        <p className="text-sm text-cyan-100">
          Civilisation One is an open scientific learning and collaboration ecosystem designed to help people learn, verify
          knowledge, conduct research, develop talent, and contribute ethically to humanity's understanding of life,
          consciousness, technology, and the universe.
        </p>
      </section>
    </div>
  );
};

export default CivilisationDashboard;
