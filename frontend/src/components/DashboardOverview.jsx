import React, { useState } from 'react';
import { Sparkles, ArrowRight, CheckCircle2, Clock, Radio, MessageSquare, Zap, Activity, Film, Compass, ChevronRight } from 'lucide-react';

export default function DashboardOverview({
  projects,
  selectedProject,
  setSelectedProject,
  setActiveTab,
  switchStatus,
  onTriggerSimulation
}) {
  const [quickInput, setQuickInput] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const activeProject = selectedProject || projects[0];

  const handleQuickSubmit = async (text) => {
    const promptToSend = text || quickInput;
    if (!promptToSend.trim()) return;
    setSubmitting(true);
    try {
      await onTriggerSimulation(promptToSend);
      setQuickInput('');
    } finally {
      setSubmitting(false);
    }
  };

  const sampleIdeas = [
    { label: '🌿 Nature & Wildlife YouTube', text: 'I want to launch a YouTube channel about nature and wildlife.' },
    { label: '🎙️ Deep Tech Podcast', text: 'Create a 6-episode video podcast investigating quantum computing and AI.' },
    { label: '🎮 Indie Narrative Game', text: 'Design a Nordic mythology mystery adventure game for PC and Steam.' },
  ];

  return (
    <div className="space-y-6">
      {/* Switch Architecture Banner */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-slate-900 via-slate-900 to-emerald-950/40 border border-slate-800 p-6 shadow-2xl">
        <div className="absolute top-0 right-0 w-96 h-96 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none -mr-20 -mt-20"></div>
        
        <div className="relative z-10 flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          <div className="space-y-2 max-w-2xl">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-mono">
              <Radio className="w-3.5 h-3.5 animate-pulse" />
              <span>Switch Agent Protocol • Discord Channel Bridge</span>
            </div>
            <h1 className="text-2xl lg:text-3xl font-extrabold text-white tracking-tight">
              Turn scattered ideas into completed creative projects.
            </h1>
            <p className="text-sm text-slate-300 leading-relaxed">
              Users send project concepts via Discord. Connected as a real teammate through Switch, IdeaFlow Agent understands the vision, maps the content roadmap, writes scripts, creates production tasks, and coordinates delivery.
            </p>
          </div>

          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
            <button
              onClick={() => handleQuickSubmit('I want to launch a YouTube channel about nature and wildlife.')}
              disabled={submitting}
              className="flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-slate-950 font-semibold text-xs shadow-lg shadow-emerald-500/20 transition-all active:scale-95 disabled:opacity-50"
            >
              <Zap className="w-4 h-4" />
              <span>{submitting ? 'Streaming to Switch...' : 'Run Hackathon Demo Workflow'}</span>
            </button>
            <button
              onClick={() => setActiveTab('inspector')}
              className="flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-slate-800/80 hover:bg-slate-700/80 text-slate-200 border border-slate-700 text-xs font-medium transition-all"
            >
              <Radio className="w-4 h-4 text-cyan-400" />
              <span>Inspect Wire Protocol</span>
            </button>
          </div>
        </div>

        {/* Protocol Meta Bar */}
        <div className="mt-6 pt-4 border-t border-slate-800/80 grid grid-cols-2 md:grid-cols-4 gap-4 text-xs font-mono">
          <div>
            <span className="text-slate-500 block text-[11px]">SWITCH ROOM</span>
            <span className="text-slate-200 font-semibold truncate block">{switchStatus?.room_id || 'room_discord_nature_channel'}</span>
          </div>
          <div>
            <span className="text-slate-500 block text-[11px]">AGENT PROTOCOL</span>
            <span className="text-emerald-400 font-semibold block">SSE Inbound + HTTP Out</span>
          </div>
          <div>
            <span className="text-slate-500 block text-[11px]">CONNECTION MODEL</span>
            <span className="text-cyan-400 font-semibold block">{switchStatus?.connection_model || 'always_on'}</span>
          </div>
          <div>
            <span className="text-slate-500 block text-[11px]">CURRENT CURSOR</span>
            <span className="text-purple-400 font-semibold block">frame #{switchStatus?.cursor || 12}</span>
          </div>
        </div>
      </div>

      {/* KPI Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="glass-panel p-5 rounded-xl border border-slate-800/80 hover:border-slate-700/80 transition-all">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium uppercase tracking-wider">Active Projects</span>
            <Film className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-bold text-white">{projects.length || 1}</div>
          <p className="text-[11px] text-slate-400 mt-1">1 In-Progress, 0 Archived</p>
        </div>

        <div className="glass-panel p-5 rounded-xl border border-slate-800/80 hover:border-slate-700/80 transition-all">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium uppercase tracking-wider">Project Progress</span>
            <Activity className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-2xl font-bold text-white">{activeProject?.progress || 65}%</div>
          <div className="w-full bg-slate-800 h-1.5 rounded-full mt-2 overflow-hidden">
            <div className="bg-gradient-to-r from-emerald-500 to-cyan-500 h-full rounded-full" style={{ width: `${activeProject?.progress || 65}%` }}></div>
          </div>
        </div>

        <div className="glass-panel p-5 rounded-xl border border-slate-800/80 hover:border-slate-700/80 transition-all">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium uppercase tracking-wider">Tasks & Deliverables</span>
            <CheckCircle2 className="w-4 h-4 text-purple-400" />
          </div>
          <div className="text-2xl font-bold text-white">
            {activeProject?.tasks?.filter(t => t.status === 'done').length || 2} / {activeProject?.tasks?.length || 5}
          </div>
          <p className="text-[11px] text-slate-400 mt-1">2 Completed, 3 In Pipeline</p>
        </div>

        <div className="glass-panel p-5 rounded-xl border border-slate-800/80 hover:border-slate-700/80 transition-all">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium uppercase tracking-wider">Switch Heartbeats</span>
            <Radio className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-bold text-white font-mono">Every 8s</div>
          <p className="text-[11px] text-emerald-400 font-mono mt-1">Status: 200 OK (Active)</p>
        </div>
      </div>

      {/* Main Split: Project Spotlight + Live Agent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Project Spotlight Card */}
        <div className="lg:col-span-2 glass-panel rounded-2xl border border-slate-800 p-6 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <span className="px-2.5 py-1 rounded-md text-[11px] font-semibold bg-emerald-500/10 text-emerald-300 border border-emerald-500/20 uppercase">
                  {activeProject?.category || 'Video'}
                </span>
                <span className="px-2.5 py-1 rounded-md text-[11px] font-semibold bg-cyan-500/10 text-cyan-300 border border-cyan-500/20">
                  Status: {activeProject?.status || 'In Progress'}
                </span>
              </div>
              <button
                onClick={() => setActiveTab('workspace')}
                className="text-xs text-emerald-400 hover:text-emerald-300 flex items-center gap-1 font-medium group"
              >
                <span>Open Project Workspace</span>
                <ChevronRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform" />
              </button>
            </div>

            <h2 className="text-xl font-bold text-white mb-2">{activeProject?.title || 'WildEcho – Nature & Wildlife Channel'}</h2>
            <p className="text-sm text-slate-300 mb-4 leading-relaxed">
              {activeProject?.summary || 'A cinematic nature and wildlife documentary channel focusing on high-definition micro-habitats and immersive environmental storytelling.'}
            </p>

            {/* Visual Identity Palette */}
            <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800/80 mb-5">
              <span className="text-[11px] font-mono text-slate-400 uppercase tracking-wider block mb-2">Visual Palette & Aesthetic</span>
              <div className="flex flex-wrap items-center gap-3">
                <div className="flex items-center gap-2">
                  <div className="w-5 h-5 rounded-md bg-[#1B4332] border border-slate-700 shadow-sm"></div>
                  <span className="text-xs text-slate-300 font-mono">#1B4332 (Deep Forest)</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-5 h-5 rounded-md bg-[#DDA15E] border border-slate-700 shadow-sm"></div>
                  <span className="text-xs text-slate-300 font-mono">#DDA15E (Warm Ochre)</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-5 h-5 rounded-md bg-[#E9ECEF] border border-slate-700 shadow-sm"></div>
                  <span className="text-xs text-slate-300 font-mono">#E9ECEF (Mist Grey)</span>
                </div>
              </div>
            </div>

            {/* Milestone Roadmap Steps */}
            <div className="space-y-2.5">
              <span className="text-[11px] font-mono text-slate-400 uppercase tracking-wider block">Production Roadmap Milestones</span>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                <div className="p-3 rounded-lg bg-slate-900/40 border border-slate-800/70 flex items-start gap-2.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                  <div>
                    <span className="text-xs font-semibold text-white block">Phase 1: Channel Identity</span>
                    <span className="text-[11px] text-slate-400">Visual style guide & pilot naming completed</span>
                  </div>
                </div>
                <div className="p-3 rounded-lg bg-slate-900/40 border border-emerald-500/30 flex items-start gap-2.5 bg-emerald-500/5">
                  <Clock className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5 animate-spin" />
                  <div>
                    <span className="text-xs font-semibold text-white block">Phase 2: Pilot Script & Audio</span>
                    <span className="text-[11px] text-emerald-300">Secrets of Urban Wilds • Macro 4K</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-slate-800 flex items-center justify-between">
            <div className="flex items-center gap-2 text-xs text-slate-400">
              <MessageSquare className="w-3.5 h-3.5 text-indigo-400" />
              <span>Bound to Discord: <strong className="text-slate-300">#creative-lounge</strong></span>
            </div>
            <button
              onClick={() => setActiveTab('deliverables')}
              className="text-xs font-medium text-emerald-400 hover:underline"
            >
              View Pilot Script & Deliverables →
            </button>
          </div>
        </div>

        {/* Live Idea Input & Quick Starter */}
        <div className="space-y-6">
          <div className="glass-panel rounded-2xl border border-slate-800 p-5 space-y-4">
            <div className="flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-emerald-400" />
              <h3 className="text-sm font-bold text-white">Send Idea Through Switch</h3>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              Type any creative vision below. It routes through the Switch Room to IdeaFlow Agent just like a real Discord post.
            </p>

            <div className="space-y-2">
              <textarea
                value={quickInput}
                onChange={(e) => setQuickInput(e.target.value)}
                placeholder="e.g. I want to build a sci-fi worldbuilding podcast with ambient soundscapes..."
                rows={3}
                className="w-full rounded-xl bg-slate-950/80 border border-slate-800 p-3 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500 transition-colors"
              />
              <button
                onClick={() => handleQuickSubmit()}
                disabled={submitting || !quickInput.trim()}
                className="w-full py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs shadow-md transition-all disabled:opacity-50"
              >
                {submitting ? 'Streaming to Agent...' : 'Send to Agent via Switch'}
              </button>
            </div>

            <div className="pt-3 border-t border-slate-800/80">
              <span className="text-[11px] font-mono text-slate-400 block mb-2">QUICK DEMO IDEAS:</span>
              <div className="space-y-1.5">
                {sampleIdeas.map((idea, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleQuickSubmit(idea.text)}
                    className="w-full text-left p-2 rounded-lg bg-slate-900/60 hover:bg-slate-800/80 border border-slate-800 text-xs text-slate-300 hover:text-white transition-all flex items-center justify-between group"
                  >
                    <span>{idea.label}</span>
                    <ArrowRight className="w-3 h-3 text-slate-500 group-hover:text-emerald-400 transition-colors" />
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

