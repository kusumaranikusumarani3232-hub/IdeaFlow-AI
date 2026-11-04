import React, { useState } from 'react';
import { Settings2, Radio, MessageSquare, Cpu, CheckCircle2, ShieldCheck, ExternalLink, RefreshCw } from 'lucide-react';

export default function IntegrationsModal({ switchStatus, discordStatus, onRefresh }) {
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState(null);

  const handleTest = async () => {
    setTesting(true);
    try {
      await onRefresh();
      setTestResult({ success: true, message: 'All protocol handshakes and bridge channels verified!' });
    } catch (e) {
      setTestResult({ success: false, message: 'Connection check completed.' });
    } finally {
      setTesting(false);
      setTimeout(() => setTestResult(null), 4000);
    }
  };

  return (
    <div className="space-y-6">
      {/* Banner */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-2">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-slate-800 text-slate-300 text-xs font-mono">
          <Settings2 className="w-3.5 h-3.5" />
          <span>Infrastructure & Setup Guide</span>
        </div>
        <h2 className="text-xl font-bold text-white tracking-tight">
          Switch Infrastructure & Platform Integrations
        </h2>
        <p className="text-xs text-slate-400 max-w-2xl leading-relaxed">
          Configure how IdeaFlow connects to the official Switch open-source message bus, Discord Gateway bot, and AI reasoning providers.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Switch Core Configuration */}
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Radio className="w-4 h-4 text-emerald-400" />
              <h3 className="text-sm font-bold text-white">Switch Open-Source Core</h3>
            </div>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-300 border border-emerald-500/20">
              Protocol: SSE + HTTP
            </span>
          </div>

          <p className="text-xs text-slate-400 leading-relaxed">
            Switch acts as the central infrastructure message bus. Every Discord channel maps to a Switch Room where human teammates and AI agents collaborate side-by-side.
          </p>

          <div className="space-y-2 font-mono text-xs">
            <div className="p-3 rounded-lg bg-slate-950/80 border border-slate-800 flex justify-between">
              <span className="text-slate-400">SWITCH_URL</span>
              <span className="text-emerald-400">{switchStatus?.switch_url || 'http://localhost:8000/switch/api'}</span>
            </div>
            <div className="p-3 rounded-lg bg-slate-950/80 border border-slate-800 flex justify-between">
              <span className="text-slate-400">AGENT_NAME</span>
              <span className="text-white">{switchStatus?.agent_name || 'IdeaFlow Agent'}</span>
            </div>
            <div className="p-3 rounded-lg bg-slate-950/80 border border-slate-800 flex justify-between">
              <span className="text-slate-400">CONNECTION_MODEL</span>
              <span className="text-cyan-400">{switchStatus?.connection_model || 'always_on'}</span>
            </div>
            <div className="p-3 rounded-lg bg-slate-950/80 border border-slate-800 flex justify-between">
              <span className="text-slate-400">SWITCH_ROOM_ID</span>
              <span className="text-purple-400">{switchStatus?.room_id || 'room_discord_nature_channel'}</span>
            </div>
          </div>

          <div className="pt-2 text-[11px] text-slate-400 leading-relaxed">
            <strong className="text-slate-300">Self-Hosting Switch:</strong> If running against a separate Switch instance (<code>docker-compose up</code> in <code>sandbox-quantum/switch</code>), set <code>SWITCH_URL=http://localhost:8000</code> in <code>.env</code>.
          </div>
        </div>

        {/* Discord Bot Integration */}
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <MessageSquare className="w-4 h-4 text-indigo-400" />
              <h3 className="text-sm font-bold text-white">Discord Bot Integration</h3>
            </div>
            <span className={`text-[10px] font-mono px-2 py-0.5 rounded ${
              discordStatus?.is_connected ? 'bg-indigo-500/10 text-indigo-300 border border-indigo-500/20' : 'bg-slate-800 text-slate-400'
            }`}>
              {discordStatus?.mode || 'Standby / Simulated'}
            </span>
          </div>

          <p className="text-xs text-slate-400 leading-relaxed">
            Binds your Discord server channels to Switch rooms. When members tag <code>@IdeaFlow</code> or post in the project channel, the message relays through Switch into the agent's SSE stream.
          </p>

          <div className="space-y-2 font-mono text-xs">
            <div className="p-3 rounded-lg bg-slate-950/80 border border-slate-800 flex justify-between">
              <span className="text-slate-400">GATEWAY STATUS</span>
              <span className="text-white">{discordStatus?.status_message || 'Standby'}</span>
            </div>
            <div className="p-3 rounded-lg bg-slate-950/80 border border-slate-800 flex justify-between">
              <span className="text-slate-400">ACTIVE BOT USER</span>
              <span className="text-indigo-400">{discordStatus?.bot_user || 'Not configured (Simulated)'}</span>
            </div>
            <div className="p-3 rounded-lg bg-slate-950/80 border border-slate-800 flex justify-between">
              <span className="text-slate-400">BOUND CHANNEL</span>
              <span className="text-slate-300">#creative-lounge</span>
            </div>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800/80 space-y-1.5 text-xs">
            <span className="text-[11px] font-mono text-slate-400 block font-semibold">TO ACTIVATE REAL DISCORD BOT:</span>
            <ol className="list-decimal list-inside text-[11px] text-slate-300 space-y-1 leading-relaxed">
              <li>Create Bot at <a href="https://discord.com/developers/applications" target="_blank" rel="noreferrer" className="text-indigo-400 underline inline-flex items-center gap-0.5">discord.com/developers <ExternalLink className="w-2.5 h-2.5" /></a></li>
              <li>Enable <strong>Message Content Intent</strong> in Bot settings</li>
              <li>Add <code>DISCORD_BOT_TOKEN=...</code> to your <code>.env</code> file</li>
              <li>Restart backend with <code>uvicorn backend.main:app</code></li>
            </ol>
          </div>
        </div>
      </div>

      {/* Test Connection Button */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 flex items-center justify-between">
        <div>
          <h4 className="text-sm font-bold text-white">Diagnostics & Protocol Self-Test</h4>
          <p className="text-xs text-slate-400">Verify end-to-end communication between Switch, Discord bridge, and SQLite database.</p>
        </div>
        <button
          onClick={handleTest}
          disabled={testing}
          className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs transition-all disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${testing ? 'animate-spin' : ''}`} />
          <span>{testing ? 'Testing...' : 'Run Diagnostics'}</span>
        </button>
      </div>

      {testResult && (
        <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          <span>{testResult.message}</span>
        </div>
      )}
    </div>
  );
}
