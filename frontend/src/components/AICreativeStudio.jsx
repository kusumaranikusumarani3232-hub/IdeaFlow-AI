import React, { useState } from 'react';
import { Sparkles, Terminal, Wand2, Copy, Check, Plus, Film, ListTodo, FileText, ArrowRight } from 'lucide-react';
import { aiBrainstorm, aiDecompose, aiGenerateScript, createTask, createDraft } from '../api';

export default function AICreativeStudio({ project, onRefreshProject }) {
  const [studioTool, setStudioTool] = useState('brainstorm'); // brainstorm | decompose | script

  // Brainstorm state
  const [concept, setConcept] = useState('YouTube channel about nature and wildlife');
  const [category, setCategory] = useState('video');
  const [vibe, setVibe] = useState('Cinematic, slow-paced, atmospheric, 4K macro');
  const [brainstormResult, setBrainstormResult] = useState('');
  const [brainstorming, setBrainstorming] = useState(false);

  // Decompose state
  const [goal, setGoal] = useState('Film outdoor pilot episode in urban park habitats');
  const [decomposeResult, setDecomposeResult] = useState('');
  const [decomposing, setDecomposing] = useState(false);

  // Script state
  const [scriptPrompt, setScriptPrompt] = useState('Episode 2: Predators of the Dusk – Night-vision forest ecology and owl behavior');
  const [scriptResult, setScriptResult] = useState('');
  const [generatingScript, setGeneratingScript] = useState(false);

  const [copied, setCopied] = useState(false);
  const [imported, setImported] = useState(false);

  const handleBrainstorm = async (e) => {
    e.preventDefault();
    setBrainstorming(true);
    setBrainstormResult('');
    try {
      const res = await aiBrainstorm(concept, category, vibe);
      setBrainstormResult(res.brainstorm_output);
    } catch (err) {
      console.error(err);
    } finally {
      setBrainstorming(false);
    }
  };

  const handleDecompose = async (e) => {
    e.preventDefault();
    setDecomposing(true);
    setDecomposeResult('');
    try {
      const res = await aiDecompose(project?.id || 'temp', goal);
      setDecomposeResult(res.tasks_breakdown);
    } catch (err) {
      console.error(err);
    } finally {
      setDecomposing(false);
    }
  };

  const handleGenerateScript = async (e) => {
    e.preventDefault();
    setGeneratingScript(true);
    setScriptResult('');
    try {
      const res = await aiGenerateScript(project?.id || 'temp', scriptPrompt);
      setScriptResult(res.script_content);
    } catch (err) {
      console.error(err);
    } finally {
      setGeneratingScript(false);
    }
  };

  const handleCopy = (text) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleSaveAsDraft = async () => {
    if (!project || !scriptResult) return;
    try {
      await createDraft(project.id, {
        project_id: project.id,
        title: `Script: ${scriptPrompt.slice(0, 45)}...`,
        draft_type: 'script',
        content: scriptResult,
        version: 1
      });
      setImported(true);
      onRefreshProject();
      setTimeout(() => setImported(false), 3000);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-6">
      {/* Studio Banner */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-mono mb-2">
            <Sparkles className="w-3.5 h-3.5" />
            <span>AI Creative Assistant Studio</span>
          </div>
          <h2 className="text-xl font-bold text-white tracking-tight">
            Brainstorm, Outline, Script, and Break Down Large Projects
          </h2>
          <p className="text-xs text-slate-400 mt-1 max-w-2xl leading-relaxed">
            Collaborate directly with the creative intelligence engine to generate concepts, break large creative milestones into smaller tasks, and write full production scripts.
          </p>
        </div>

        {/* Tool selector buttons */}
        <div className="flex items-center gap-1.5 p-1 bg-slate-900/80 rounded-xl border border-slate-800 self-start md:self-auto">
          <button
            onClick={() => setStudioTool('brainstorm')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              studioTool === 'brainstorm' ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' : 'text-slate-400 hover:text-white'
            }`}
          >
            <Wand2 className="w-3.5 h-3.5" />
            <span>Brainstorm Concept</span>
          </button>
          <button
            onClick={() => setStudioTool('decompose')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              studioTool === 'decompose' ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' : 'text-slate-400 hover:text-white'
            }`}
          >
            <ListTodo className="w-3.5 h-3.5" />
            <span>Decompose Goal</span>
          </button>
          <button
            onClick={() => setStudioTool('script')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              studioTool === 'script' ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' : 'text-slate-400 hover:text-white'
            }`}
          >
            <FileText className="w-3.5 h-3.5" />
            <span>Write Script</span>
          </button>
        </div>
      </div>

      {/* Tool 1: Brainstorm Concept */}
      {studioTool === 'brainstorm' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <Wand2 className="w-4 h-4 text-emerald-400" />
              <span>Brand Identity & Name Ideator</span>
            </h3>
            <form onSubmit={handleBrainstorm} className="space-y-4">
              <div>
                <label className="text-[11px] font-mono text-slate-400 block mb-1">PROJECT CONCEPT</label>
                <input
                  type="text"
                  value={concept}
                  onChange={(e) => setConcept(e.target.value)}
                  placeholder="e.g. YouTube channel about nature and wildlife"
                  className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-xs text-white"
                  required
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-[11px] font-mono text-slate-400 block mb-1">CATEGORY</label>
                  <select
                    value={category}
                    onChange={(e) => setCategory(e.target.value)}
                    className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-xs text-white"
                  >
                    <option value="video">YouTube / Video</option>
                    <option value="podcast">Podcast / Audio</option>
                    <option value="writing">Book / Writing</option>
                    <option value="game">Video Game</option>
                    <option value="brand">Brand / Creative Studio</option>
                  </select>
                </div>
                <div>
                  <label className="text-[11px] font-mono text-slate-400 block mb-1">DESIRED VIBE</label>
                  <input
                    type="text"
                    value={vibe}
                    onChange={(e) => setVibe(e.target.value)}
                    placeholder="e.g. Cinematic, slow-paced, 4K"
                    className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-xs text-white"
                  />
                </div>
              </div>
              <button
                type="submit"
                disabled={brainstorming || !concept.trim()}
                className="w-full py-2.5 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-slate-950 font-bold text-xs shadow-md transition-all disabled:opacity-50"
              >
                {brainstorming ? 'Brainstorming with AI Agent...' : 'Generate Brand Concept & Identity'}
              </button>
            </form>
          </div>

          {/* Brainstorm Output */}
          <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-white uppercase tracking-wider">Generated Identity</h3>
              {brainstormResult && (
                <button
                  onClick={() => handleCopy(brainstormResult)}
                  className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-white"
                >
                  {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                  <span>{copied ? 'Copied' : 'Copy'}</span>
                </button>
              )}
            </div>
            <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800/80 text-xs text-slate-200 leading-relaxed min-h-[220px] max-h-[420px] overflow-y-auto whitespace-pre-wrap font-mono">
              {brainstormResult || 'Click "Generate Brand Concept & Identity" to brainstorm channel names, taglines, color palettes, and audience targeting.'}
            </div>
          </div>
        </div>
      )}

      {/* Tool 2: Decompose Goal */}
      {studioTool === 'decompose' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <ListTodo className="w-4 h-4 text-cyan-400" />
              <span>Milestone Task Decomposition</span>
            </h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Break down any large creative goal or milestone into actionable, prioritized production tasks.
            </p>
            <form onSubmit={handleDecompose} className="space-y-4">
              <div>
                <label className="text-[11px] font-mono text-slate-400 block mb-1">CREATIVE GOAL OR MILESTONE</label>
                <textarea
                  value={goal}
                  onChange={(e) => setGoal(e.target.value)}
                  placeholder="e.g. Set up high-fidelity binaural forest Foley recording system"
                  rows={3}
                  className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-xs text-white"
                  required
                />
              </div>
              <button
                type="submit"
                disabled={decomposing || !goal.trim()}
                className="w-full py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-teal-500 hover:from-cyan-400 hover:to-teal-400 text-slate-950 font-bold text-xs shadow-md transition-all disabled:opacity-50"
              >
                {decomposing ? 'Decomposing Goal...' : 'Break Down into Actionable Tasks'}
              </button>
            </form>
          </div>

          <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-white uppercase tracking-wider">Decomposed Tasks</h3>
              {decomposeResult && (
                <button
                  onClick={() => handleCopy(decomposeResult)}
                  className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-white"
                >
                  {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                  <span>{copied ? 'Copied' : 'Copy'}</span>
                </button>
              )}
            </div>
            <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800/80 text-xs text-slate-200 leading-relaxed min-h-[220px] max-h-[420px] overflow-y-auto whitespace-pre-wrap font-mono">
              {decomposeResult || 'Input a milestone and click "Break Down into Actionable Tasks" to generate categorized steps.'}
            </div>
          </div>
        </div>
      )}

      {/* Tool 3: Write Script */}
      {studioTool === 'script' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <FileText className="w-4 h-4 text-purple-400" />
              <span>Cinematic Video / Podcast Scriptwriter</span>
            </h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Generate screenplay drafts with timestamps, camera angles, macro visual cues, and binaural audio design.
            </p>
            <form onSubmit={handleGenerateScript} className="space-y-4">
              <div>
                <label className="text-[11px] font-mono text-slate-400 block mb-1">EPISODE TOPIC OR HOOK</label>
                <textarea
                  value={scriptPrompt}
                  onChange={(e) => setScriptPrompt(e.target.value)}
                  placeholder="e.g. Episode 2: Predators of the Dusk – Night-vision forest ecology and owl behavior"
                  rows={3}
                  className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-xs text-white"
                  required
                />
              </div>
              <button
                type="submit"
                disabled={generatingScript || !scriptPrompt.trim()}
                className="w-full py-2.5 rounded-xl bg-gradient-to-r from-purple-500 to-indigo-500 hover:from-purple-400 hover:to-indigo-400 text-white font-bold text-xs shadow-md transition-all disabled:opacity-50"
              >
                {generatingScript ? 'Writing Cinematic Script...' : 'Generate Full Episode Script'}
              </button>
            </form>
          </div>

          <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-white uppercase tracking-wider">Script Draft</h3>
              <div className="flex items-center gap-2">
                {scriptResult && (
                  <>
                    <button
                      onClick={handleSaveAsDraft}
                      className="flex items-center gap-1 px-2.5 py-1 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 text-xs font-mono"
                    >
                      <Plus className="w-3 h-3" />
                      <span>{imported ? 'Saved to Project!' : 'Save to Project'}</span>
                    </button>
                    <button
                      onClick={() => handleCopy(scriptResult)}
                      className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-white"
                    >
                      {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                      <span>{copied ? 'Copied' : 'Copy'}</span>
                    </button>
                  </>
                )}
              </div>
            </div>
            <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800/80 text-xs text-slate-200 leading-relaxed min-h-[220px] max-h-[420px] overflow-y-auto whitespace-pre-wrap font-mono">
              {scriptResult || 'Enter an episode topic and click "Generate Full Episode Script" to produce audio-visual directions and narration.'}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

