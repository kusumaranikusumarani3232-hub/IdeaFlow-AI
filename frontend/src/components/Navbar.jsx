import React from 'react';
import { Sparkles, Radio, MessageSquare, Terminal, FolderKanban, CheckCircle2, Settings2 } from 'lucide-react';

export default function Navbar({ activeTab, setActiveTab, switchStatus, discordStatus, demoMode, setDemoMode }) {
  const isSwitchOnline = Boolean(switchStatus?.is_connected);
  const isDiscordLive = discordStatus?.is_connected ?? false;

  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: FolderKanban },
    { id: 'workspace', label: 'Workspace', icon: Sparkles },
    { id: 'studio', label: 'AI Creative Studio', icon: Terminal },
    { id: 'inspector', label: 'Switch Inspector', icon: Radio, highlight: true },
    { id: 'deliverables', label: 'Deliverables', icon: CheckCircle2 },
    { id: 'settings', label: 'Integrations', icon: Settings2 },
  ];

  return (
    <header className="sticky top-0 z-50 glass-panel border-b border-slate-800/80 px-4 lg:px-8 py-3.5">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-3">
        {/* Brand identity */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-500 via-teal-500 to-cyan-500 flex items-center justify-center shadow-lg shadow-emerald-500/20">
            <Sparkles className="w-5 h-5 text-slate-950 font-bold" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xl font-bold tracking-tight text-white">IdeaFlow<span className="text-emerald-400">.ai</span></span>
              <span className="text-[10px] uppercase font-semibold px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-300 border border-emerald-500/20">
                Hackathon 2026
              </span>
            </div>
            <p className="text-xs text-slate-400">Creative Project Manager powered by Switch</p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="flex items-center gap-1 overflow-x-auto p-1 bg-slate-900/60 rounded-xl border border-slate-800/80">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium transition-all duration-150 whitespace-nowrap ${
                  isActive
                    ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 shadow-sm'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                } ${item.highlight && !isActive ? 'text-cyan-400 font-semibold' : ''}`}
              >
                <Icon className={`w-3.5 h-3.5 ${isActive ? 'text-emerald-400' : item.highlight ? 'text-cyan-400 animate-pulse' : 'text-slate-400'}`} />
                <span>{item.label}</span>
                {item.highlight && (
                  <span className="text-[9px] px-1 py-0.2 rounded bg-cyan-500/20 text-cyan-300 font-mono">
                    Protocol
                  </span>
                )}
              </button>
            );
          })}
        </nav>

        {/* Infrastructure Status Indicators */}
        <div className="flex items-center gap-2">
          {/* Switch Status Badge with Mode distinction */}
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-slate-900/80 border border-slate-700/60 text-xs">
            <span className="relative flex h-2 w-2">
              <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${isSwitchOnline ? 'bg-emerald-400' : 'bg-rose-400'}`}></span>
              <span className={`relative inline-flex rounded-full h-2 w-2 ${isSwitchOnline ? 'bg-emerald-500' : 'bg-rose-500'}`}></span>
            </span>
            <span className="text-slate-400 font-mono text-[11px]">Switch:</span>
            <span className={`font-semibold font-mono text-[11px] ${isSwitchOnline ? 'text-emerald-400' : 'text-rose-400'}`}>
              {switchStatus?.is_builtin ? 'Built-in Hub' : (isSwitchOnline ? 'Official Switch (Live)' : 'External (Offline)')}
            </span>
          </div>

          {/* Discord Status Badge */}
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-slate-900/80 border border-slate-700/60 text-xs">
            <MessageSquare className={`w-3 h-3 ${isDiscordLive ? 'text-indigo-400' : 'text-slate-400'}`} />
            <span className="text-slate-400 font-mono text-[11px]">Discord:</span>
            <span className={`font-mono text-[11px] ${isDiscordLive ? 'text-indigo-400 font-semibold' : 'text-slate-400'}`}>
              {isDiscordLive ? 'Gateway' : 'Simulated'}
            </span>
          </div>

          {/* Demo Mode Status Indicator */}
          <button
            onClick={() => setDemoMode(!demoMode)}
            className={`px-2 py-1 rounded-md text-[11px] font-mono border transition-all ${
              demoMode
                ? 'bg-purple-500/10 text-purple-300 border-purple-500/30'
                : 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
            }`}
            title={demoMode ? "Demo simulation active" : "Real External Switch Integration Active"}
          >
            Demo: {demoMode ? 'ON' : 'OFF'}
          </button>
        </div>
      </div>
    </header>
  );
}

