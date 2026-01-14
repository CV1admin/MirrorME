import React, { useState, useRef, useEffect, useMemo } from 'react';
import { Message, Role, MessageStatus, AuditMetadata, SimulationState } from '../types';
import { sendMessageStream } from '../services/geminiService';

interface ChatInterfaceProps {
  simState?: SimulationState;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ simState }) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'boot-001',
      role: Role.ASSISTANT,
      content: 'Cognitive Flight Recorder Auditor [MKone-CFR-01] online. Ready for neural audit protocol initiation.',
      timestamp: new Date(),
      status: 'ack',
      audit: {
        module_id: "MKone-CFR-01",
        assumptions: ["System invariants stable"],
        constraints_checked: ["Truth-layer link"],
        violations: [],
        confidence: 1.0,
        refs: ["MIRROR_INIT_0"]
      }
    }
  ]);
  const [input, setInput] = useState('');
  const [isAuditMode, setIsAuditMode] = useState(true);
  const [selectedMsgId, setSelectedMsgId] = useState<string | null>('boot-001');
  const [isAutoScroll, setIsAutoScroll] = useState(true);

  const scrollRef = useRef<HTMLDivElement>(null);

  const selectedMessage = useMemo(() => 
    messages.find(m => m.id === selectedMsgId), 
  [messages, selectedMsgId]);

  useEffect(() => {
    if (isAutoScroll && scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isAutoScroll]);

  const handleScroll = () => {
    if (!scrollRef.current) return;
    const { scrollTop, scrollHeight, clientHeight } = scrollRef.current;
    const isAtBottom = scrollHeight - scrollTop - clientHeight < 50;
    setIsAutoScroll(isAtBottom);
  };

  const executeCommand = (cmd: string) => {
    const [name, ...args] = cmd.slice(1).split(' ');
    console.log(`Executing slash command: ${name}`, args);
    // Placeholder for actual command integration with sim runner
    return `Command /${name} processed. Logic gate updated.`;
  };

  const handleSend = async () => {
    if (!input.trim()) return;

    const currentInput = input;
    setInput('');
    
    if (currentInput.startsWith('/')) {
      const response = executeCommand(currentInput);
      setMessages(prev => [...prev, {
        id: crypto.randomUUID(),
        role: Role.SYSTEM,
        content: response,
        timestamp: new Date(),
        status: 'ack'
      }]);
      return;
    }

    const clientMsgId = crypto.randomUUID();
    const assistantId = crypto.randomUUID();

    const userMsg: Message = {
      id: crypto.randomUUID(),
      client_msg_id: clientMsgId,
      role: Role.USER,
      content: currentInput,
      timestamp: new Date(),
      status: 'pending'
    };

    setMessages(prev => [...prev, userMsg]);
    setIsAutoScroll(true);

    const assistantPlaceholder: Message = {
      id: assistantId,
      role: Role.ASSISTANT,
      content: '',
      timestamp: new Date(),
      status: 'streaming'
    };

    // Fix: cast 'ack' to MessageStatus to avoid type widening to 'string' in the spread object
    setMessages(prev => prev.map(m => m.id === userMsg.id ? { ...m, status: 'ack' as MessageStatus } : m).concat(assistantPlaceholder));

    let accumulatedText = "";
    const currentMetrics = simState?.metrics[simState.metrics.length - 1];
    const stream = sendMessageStream([...messages, userMsg], currentMetrics);

    for await (const chunk of stream) {
      if (!chunk.done) {
        accumulatedText += chunk.text;
        setMessages(prev => prev.map(m => 
          m.id === assistantId ? { ...m, content: accumulatedText } : m
        ));
      } else {
        setMessages(prev => prev.map(m => 
          m.id === assistantId ? { 
            ...m, 
            status: 'sent', 
            audit: chunk.audit 
          } : m
        ));
      }
    }
  };

  return (
    <div className="h-full flex bg-slate-900 overflow-hidden">
      {/* Panel 1: Main Stream */}
      <div className={`flex flex-col flex-1 border-r border-slate-800 transition-all ${selectedMsgId ? 'w-1/2' : 'w-full'}`}>
        <header className="p-3 border-b border-slate-800 flex items-center justify-between bg-slate-900/60 backdrop-blur">
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${messages.some(m => m.status === 'streaming') ? 'bg-indigo-400 animate-pulse' : 'bg-cyan-500'}`} />
            <h3 className="text-[10px] font-black uppercase tracking-[0.2em] text-slate-400">Audit Link</h3>
          </div>
          <button 
            onClick={() => setIsAuditMode(!isAuditMode)}
            className={`px-2 py-0.5 rounded text-[8px] font-bold uppercase transition-all border ${
              isAuditMode ? 'bg-indigo-500/20 text-indigo-400 border-indigo-500/30' : 'bg-slate-800 text-slate-500 border-slate-700'
            }`}
          >
            Audit Mode: {isAuditMode ? 'ON' : 'OFF'}
          </button>
        </header>

        <div 
          ref={scrollRef} 
          onScroll={handleScroll}
          className="flex-1 overflow-y-auto p-4 space-y-4 scrollbar-hide"
        >
          {messages.map((m) => (
            <div 
              key={m.id} 
              onClick={() => setSelectedMsgId(m.id)}
              className={`flex flex-col gap-1 group cursor-pointer ${m.role === Role.USER ? 'items-end' : 'items-start'}`}
            >
              <div className={`max-w-[85%] px-4 py-2.5 rounded-xl text-sm transition-all border ${
                m.role === Role.USER 
                ? 'bg-slate-800 text-slate-100 border-slate-700 rounded-tr-none' 
                : m.role === Role.SYSTEM
                ? 'bg-slate-900/50 text-indigo-400 border-indigo-500/20 italic text-xs'
                : 'bg-slate-950/80 text-slate-300 border-slate-800 rounded-tl-none'
              } ${selectedMsgId === m.id ? 'ring-1 ring-cyan-500/50' : ''}`}>
                <div className="whitespace-pre-wrap">{m.content.split('AUDIT_BLOCK')[0].trim()}</div>
                {m.status === 'streaming' && <span className="inline-block w-1.5 h-4 ml-1 bg-indigo-500 animate-pulse align-middle" />}
              </div>
              <div className="flex items-center gap-2 px-1">
                <span className="text-[9px] font-bold text-slate-600 uppercase">
                  {m.role === Role.USER ? 'Researcher' : m.role === Role.SYSTEM ? 'System' : 'Auditor'}
                </span>
                {m.audit && isAuditMode && <span className="text-[8px] text-indigo-400 font-black">AUDITED</span>}
                {m.status === 'pending' && <span className="text-[8px] text-slate-500 animate-pulse">SENDING...</span>}
              </div>
            </div>
          ))}
        </div>

        <div className="p-4 bg-slate-950 border-t border-slate-800">
          <div className="relative group">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend(); }
              }}
              placeholder="Command (e.g. /run, /metrics) or audit query..."
              className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-cyan-500 resize-none transition-all pr-12 min-h-[50px] max-h-[150px] scrollbar-hide"
              rows={1}
            />
            <button 
              onClick={handleSend}
              disabled={!input.trim() || messages.some(m => m.status === 'streaming')}
              className="absolute right-3 bottom-3 text-cyan-500 hover:text-cyan-400 disabled:opacity-20 p-1"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            </button>
          </div>
        </div>
      </div>

      {/* Panel 2: Inspector */}
      {selectedMsgId && (
        <div className="w-1/2 bg-slate-950 flex flex-col animate-in slide-in-from-right duration-200">
          <header className="p-3 border-b border-slate-800 flex items-center justify-between">
            <h4 className="text-[10px] font-black uppercase tracking-widest text-slate-500">Cognitive Inspector</h4>
            <button onClick={() => setSelectedMsgId(null)} className="text-slate-600 hover:text-slate-300">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
            </button>
          </header>

          <div className="flex-1 overflow-y-auto p-4 space-y-6 scrollbar-hide">
            {selectedMessage?.audit ? (
              <div className="space-y-6">
                <div>
                  <h5 className="text-[9px] uppercase font-bold text-slate-600 mb-3 tracking-wider">Confidence Protocol</h5>
                  <div className="flex items-center gap-4">
                    <div className="flex-1 h-1 bg-slate-800 rounded-full overflow-hidden">
                      <div className="h-full bg-cyan-500 transition-all duration-1000" style={{ width: `${selectedMessage.audit.confidence * 100}%` }} />
                    </div>
                    <span className="text-xs font-black mono text-cyan-400">{(selectedMessage.audit.confidence * 100).toFixed(0)}%</span>
                  </div>
                </div>

                <section className="space-y-3">
                  <h5 className="text-[9px] uppercase font-bold text-slate-600 tracking-wider">Audit Trace Summary</h5>
                  <div className="grid grid-cols-1 gap-2">
                    {selectedMessage.audit.assumptions.map((a, i) => (
                      <div key={i} className="text-[10px] text-slate-400 bg-slate-900 border border-slate-800 p-2 rounded flex items-start gap-2">
                        <span className="text-indigo-500 font-bold">A:</span> {a}
                      </div>
                    ))}
                    {selectedMessage.audit.constraints_checked.map((c, i) => (
                      <div key={i} className="text-[10px] text-emerald-400/80 bg-emerald-500/5 border border-emerald-500/10 p-2 rounded flex items-start gap-2">
                         <svg className="w-3 h-3 mt-0.5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" /></svg>
                         {c}
                      </div>
                    ))}
                  </div>
                </section>

                {selectedMessage.audit.violations.length > 0 && (
                   <section className="space-y-2">
                    <h5 className="text-[9px] uppercase font-bold text-rose-500 tracking-wider">Invariant Violations</h5>
                    {selectedMessage.audit.violations.map((v, i) => (
                      <div key={i} className="text-[10px] text-rose-400 bg-rose-500/5 border border-rose-500/10 p-2 rounded font-mono">
                        {v}
                      </div>
                    ))}
                  </section>
                )}

                <section className="space-y-2">
                  <h5 className="text-[9px] uppercase font-bold text-slate-600 tracking-wider">Trace References</h5>
                  <div className="flex flex-wrap gap-1.5">
                    {selectedMessage.audit.refs.map((r, i) => (
                      <span key={i} className="px-2 py-0.5 bg-slate-900 border border-slate-800 rounded text-[9px] font-mono text-indigo-400">
                        {r}
                      </span>
                    ))}
                  </div>
                </section>
              </div>
            ) : (
              <div className="h-full flex flex-col items-center justify-center text-center opacity-30">
                <svg className="w-12 h-12 mb-4 text-slate-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                </svg>
                <p className="text-xs uppercase tracking-widest font-black text-slate-600">No Trace Artifact Selected</p>
                <p className="text-[10px] mt-2 text-slate-700">Audit logs require a signed assistant message.</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatInterface;