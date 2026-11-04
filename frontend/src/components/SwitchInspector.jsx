import React, { useState, useEffect } from 'react';
import { Radio, RefreshCw, Send, CheckCircle2, AlertCircle, ArrowUpRight, ArrowDownLeft, Cpu, Terminal, ShieldCheck } from 'lucide-react';
import { fetchSwitchStatus, fetchSwitchEvents, sendManualBeat, simulateDiscordMessage } from '../api';

export default function SwitchInspector({ switchStatus, onRefreshStatus }) {
  const [events, setEvents] = useState([]);
  const [loadingEvents, setLoadingEvents] = useState(false);
  const [simText, setSimText] = useState('I want to plan Episode 2 about nocturnal predators in the forest.');
  const [simAuthor, setSimAuthor] = useState('Alex (Creator)');
  const [transmitting, setTransmitting] = useState(false);
  const [beatResult, setBeatResult] = useState(null);

  const loadEvents = async () => {
    setLoadingEvents(true);
    try {
      const data = await fetchSwitchEvents(40);
      setEvents(data);
    } catch (e) {
      console.error('Error fetching switch events:', e);
    } finally {
      setLoadingEvents(false);
    }
  };

  useEffect(() => {
    loadEvents();
    const interval = setInterval(loadEvents, 4000);
    return () => clearInterval(interval);
  }, []);

  const handleSendSimulation = async (e) => {
    e.preventDefault();
    if (!simText.trim()) return;
    setTransmitting(true);
    try {
      await simulateDiscordMessage(simText, simAuthor);
      await loadEvents();
      if (onRefreshStatus) onRefreshStatus();
    } catch (err) {
      console.error(err);
    } finally {
      setTransmitting(false);
    }
  };

  const handleManualBeat = async () => {
    try {
      const res = await sendManualBeat();
      setBeatResult(res);
      await loadEvents();
      setTimeout(() => setBeatResult(null), 3000);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Protocol Spec Header */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 text-xs font-mono">
              <Radio className="w-3.5 h-3.5 animate-pulse" />
              <span>Official Switch Agent Protocol v1.0 • Wire Inspector</span>
            </div>
            <h2 className="text-xl font-bold text-white tracking-tight">
              Switch Core Infrastructure & Protocol Telemetry
            </h2>
            <p className="text-xs text-slate-400 max-w-2xl leading-relaxed">
              IdeaFlow AI natively implements the SandboxAQ Switch agent specification: Server-Sent Events (SSE) inbound stream, HTTP heartbeat cursor management, and room outbound message posting.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleManualBeat}
              className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-purple-500/10 hover:bg-purple-500/20 text-purple-300 border border-purple-500/30 text-xs font-mono transition-all"
            >
              <Cpu className="w-3.5 h-3.5" />
              <span>{beatResult ? 'Heartbeat Beat OK!' : 'Trigger Beat'}</span>
            </button>
            <button
              onClick={loadEvents}
              disabled={loadingEvents}
              className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-mono transition-all"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loadingEvents ? 'animate-spin' : ''}`} />
              <span>Refresh Wire</span>
            </button>
          </div>
        </div>

        {/* Protocol Spec Telemetry Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-4 border-t border-slate-800 font-mono text-xs">
          <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800/80">
            <span className="text-slate-500 text-[10px] block">SWITCH ENGINE MODE</span>
            <span className="text-emerald-400 font-semibold truncate block">
              {switchStatus?.is_builtin ? '● Built-in Hub Engine' : '○ External Official Switch'}
            </span>
          </div>
          <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800/80">
            <span className="text-slate-500 text-[10px] block">AGENT ID</span>
            <span className="text-white font-semibold truncate block">{switchStatus?.agent_id || 'agent_ideaflow_creative_01'}</span>
          </div>
          <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800/80">
            <span className="text-slate-500 text-[10px] block">TRANSPORT</span>
            <span className="text-emerald-400 font-semibold block">SSE (Down) + HTTP (Up)</span>
          </div>
          <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800/80">
            <span className="text-slate-500 text-[10px] block">CONNECTION MODEL</span>
            <span className="text-cyan-400 font-semibold block">{switchStatus?.connection_model || 'always_on'}</span>
          </div>
        </div>

      </div>

      {/* Simulator + Wire Log Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Discord Simulator Box */}
        <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-4">
          <div className="flex items-center gap-2">
            <Terminal className="w-4 h-4 text-emerald-400" />
            <h3 className="text-sm font-bold text-white">Discord Inbound Simulator</h3>
          </div>
          <p className="text-xs text-slate-400 leading-relaxed">
            Send a message as a Discord creator. It enters the Switch Room, triggers an inbound SSE frame, and the IdeaFlow Agent generates tasks and responds back.
          </p>

          <form onSubmit={handleSendSimulation} className="space-y-3">
            <div>
              <label className="text-[11px] font-mono text-slate-400 block mb-1">AUTHOR NAME</label>
              <input
                type="text"
                value={simAuthor}
                onChange={(e) => setSimAuthor(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-xs text-white"
              />
            </div>
            <div>
              <label className="text-[11px] font-mono text-slate-400 block mb-1">DISCORD CHANNEL</label>
              <input
                type="text"
                disabled
                value="#creative-lounge"
                className="w-full px-3 py-2 rounded-lg bg-slate-950/50 border border-slate-800 text-xs text-slate-500 font-mono"
              />
            </div>
            <div>
              <label className="text-[11px] font-mono text-slate-400 block mb-1">MESSAGE CONTENT</label>
              <textarea
                value={simText}
                onChange={(e) => setSimText(e.target.value)}
                rows={4}
                className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500"
              />
            </div>
            <button
              type="submit"
              disabled={transmitting || !simText.trim()}
              className="w-full py-2.5 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-slate-950 font-bold text-xs shadow-md transition-all active:scale-95 disabled:opacity-50"
            >
              {transmitting ? 'Transmitting to Switch...' : 'Transmit through Switch Room'}
            </button>
          </form>

          <div className="pt-3 border-t border-slate-800 space-y-2">
            <span className="text-[11px] font-mono text-slate-400 block">TRY QUICK PROMPTS:</span>
            <button
              type="button"
              onClick={() => setSimText('Create a 4-week YouTube upload schedule for our wildlife channel.')}
              className="w-full text-left p-2 rounded bg-slate-900/50 hover:bg-slate-800 text-[11px] text-slate-300 truncate block"
            >
              📅 4-Week YouTube upload schedule
            </button>
            <button
              type="button"
              onClick={() => setSimText('Suggest 3 title and thumbnail ideas designed for high CTR.')}
              className="w-full text-left p-2 rounded bg-slate-900/50 hover:bg-slate-800 text-[11px] text-slate-300 truncate block"
            >
              🎯 3 High-CTR Title & Thumbnails
            </button>
          </div>
        </div>

        {/* Live Wire Event Logs */}
        <div className="lg:col-span-2 glass-panel p-5 rounded-2xl border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Radio className="w-4 h-4 text-cyan-400" />
              <h3 className="text-sm font-bold text-white">Live Switch Wire Traffic</h3>
            </div>
            <span className="text-xs font-mono text-slate-400">
              {events.length} packets logged
            </span>
          </div>

          <div className="space-y-2.5 max-h-[520px] overflow-y-auto pr-2 font-mono text-xs">
            {events.length === 0 ? (
              <div className="text-center py-12 text-slate-500 text-xs">
                No frames captured yet. Click "Transmit through Switch" or "Trigger Beat".
              </div>
            ) : (
              events.map((evt) => {
                const isInbound = evt.direction === 'INBOUND';
                const isOutbound = evt.direction === 'OUTBOUND';
                return (
                  <div
                    key={evt.id}
                    className="p-3 rounded-xl bg-slate-950/70 border border-slate-800/80 hover:border-slate-700 transition-all space-y-2"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                          isInbound
                            ? 'bg-emerald-500/10 text-emerald-300 border border-emerald-500/20'
                            : isOutbound
                            ? 'bg-cyan-500/10 text-cyan-300 border border-cyan-500/20'
                            : 'bg-slate-800 text-slate-300'
                        }`}>
                          {isInbound ? '⬇ INBOUND' : '⬆ OUTBOUND'}
                        </span>
                        <span className="text-white font-semibold">{evt.event_type}</span>
                        <span className="text-[10px] text-slate-500">cursor: #{evt.cursor}</span>
                      </div>
                      <span className="text-[10px] text-slate-500">
                        {evt.timestamp ? new Date(evt.timestamp).toLocaleTimeString() : ''}
                      </span>
                    </div>

                    <div className="p-2 rounded bg-slate-900/60 border border-slate-800 text-[11px] text-slate-300 leading-relaxed overflow-x-auto whitespace-pre-wrap">
                      {typeof evt.payload === 'object' ? JSON.stringify(evt.payload, null, 2) : evt.payload}
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

